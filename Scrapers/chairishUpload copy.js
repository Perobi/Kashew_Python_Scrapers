const axios = require("axios");
const moment = require("moment");
const User = require("../models/User.js");
const Listing = require("../models/Listing.js");
const Store = require("../models/Store.js");
const MktModel = require("../models/MktModel.js");
const {
  csvDescriptionReplacements,
} = require("./csvDescriptionReplacements.js");
const { errorBugSlack, bulkUploadSlack } = require(`../routes/slackNots.js`);
const { updateListingsStore } = require("./updateListingsStore.js");
const { processNewListing } = require("./UploadCSVListing.js");
const { createUniqueListing } = require("./uniqueKashewId.js");
const { emitSocketEvent } = require("./redisEventEmitter.js");
const { getNewSchema } = require("./getNewSchema.js");
const RemovedListing = require("../models/RemovedListing.js");
const { decodeEntities } = require("./utils.js");
const cheerio = require("cheerio");
const { compareCSVListing } = require("./compareCSVListing.js");
const { notifyOfPriceChange } = require("./notifyOfPriceChange.js");

const chairishImportProducts = async (storeUrl) => {
  try {
    if (!storeUrl) return null;
    // Fetch user account page
    let htmlPage = await axios
      .get(`${storeUrl}?page_size=96`)
      .then((res) => {
        return res.data;
      })
      .catch(async (err) => {
        console.log(err?.response?.data ? err.response.data : err);
        return await axios
          .get(`${storeUrl}?page_size=96`)
          .then((res) => {
            return res.data;
          })
          .catch((err) => {
            console.log(err?.response?.data ? err.response.data : err);
            return null;
          });
      });

    if (!htmlPage) return null;

    const $ = cheerio.load(htmlPage);

    // Extract number of pages
    const $paginationSummary = $(".pagination-summary");

    let pagesNumber = 0;
    if ($paginationSummary) {
      let pagesText = $(".pagination-summary").text().trim();
      if (pagesText) {
        pagesNumber = parseInt(pagesText.replace("Displaying page 1 of ", ""));
      } else {
        pagesNumber = 1;
      }
    } else {
      pagesNumber = 1;
    }
    // Loop through pages and extract product details

    let products = [];
    for (let i = 0; i < pagesNumber; i++) {
      let productsPage = await axios
        .get(`${storeUrl}?page_size=96&page=${i + 1}`)
        .then((res) => {
          return res.data;
        })
        .catch(async (err) => {
          console.log(err?.response?.data ? err.response.data : err);
          return await axios
            .get(`${storeUrl}?page_size=96&page=${i + 1}`)
            .then((res) => {
              return res.data;
            })
            .catch((err) => {
              console.log(err?.response?.data ? err.response.data : err);
              return null;
            });
        });

      if (!productsPage) break;

      const $cheerioProductsPage = cheerio.load(productsPage);
      const $productsGridContainer = $cheerioProductsPage(
        ".product-grid-container "
      );

      const $divs = $productsGridContainer.find(".js-product");

      for (let div of $divs) {
        await new Promise((resolve) => setTimeout(resolve, 500));

        let url = div.attribs["data-product-url"];
        let id = div.attribs["data-product-id"];
        let productPage = await axios
          .get(`https://www.chairish.com${url}`)
          .then((res) => {
            return res.data;
          })
          .catch(async (err) => {
            console.log(err?.response?.data ? err.response.data : err);
            return await axios
              .get(`https://www.chairish.com${url}`)
              .then((res) => {
                return res.data;
              })
              .catch((err) => {
                console.log(err?.response?.data ? err.response.data : err);
                return null;
              });
          });

        let tearSheetPage = await axios
          .get(`https://www.chairish.com/product/${id}/tear-sheet`)
          .then((res) => {
            return res.data;
          })
          .catch(async (err) => {
            console.log(err?.response?.data ? err.response.data : err);
            return await axios
              .get(`https://www.chairish.com/product/${id}/tear-sheet`)
              .then((res) => {
                return res.data;
              })
              .catch((err) => {
                console.log(err?.response?.data ? err.response.data : err);
                return null;
              });
          });

        let $cheerioProductPage;

        try {
          if (productPage) {
            $cheerioProductPage = cheerio.load(productPage);
          }
        } catch (err) {
          console.log(err);
        }

        if (!$cheerioProductPage) continue;

        let $cheerioTearSheetPage;
        if (tearSheetPage) {
          $cheerioTearSheetPage = cheerio.load(tearSheetPage);
        }

        const ldJsonScript = $cheerioProductPage(
          'script[type="application/ld+json"]'
        ).eq(1);
        const ldJson = JSON.parse(ldJsonScript.html());

        // title
        const title = $cheerioProductPage(".product-title").text().trim();
        // description
        const description = $cheerioProductPage(
          ".js-swap-sibling.js-toggle-less.hidden"
        )
          .text()
          .trim()
          .replace(/less/g, "");
        // price
        const price = $cheerioProductPage(
          ".product-price-current .product-price-value"
        )
          .text()
          .trim()
          .replace(/[,$]/g, "");
        // retailPrice
        const retailPrice = $cheerioProductPage(
          ".product-price-previous .product-price-value"
        )
          .text()
          .trim()
          .replace(/[,$]/g, "");
        // images
        const images = $cheerioProductPage(".carousel-indicators img")
          .map(function () {
            return $(this).attr("src")?.split("?")[0];
          })
          .get();

        // link
        const link = ldJson?.url;
        // category
        const category = $cheerioProductPage(".breadcrumb-wrapper")
          ?.find("li")
          ?.eq(-2)
          ?.text();

        // brand
        const brand = ldJson?.brand?.name;
        // width
        const width = ldJson?.width?.value;
        // height
        const height = ldJson?.height?.value;
        // depth
        const depth = ldJson?.depth?.value;
        // location
        const location = $cheerioProductPage(".js-product-ships-from")
          .text()
          .replace(/Est. Arrival from/g, "")
          .trim();
        // SKU
        let SKU;
        if ($cheerioTearSheetPage) {
          SKU = $cheerioTearSheetPage(".print-column-group")
            .filter((i, el) => {
              return (
                $(el).find("h2").text().trim() === "Seller Reference Number"
              );
            })
            .find("p")
            .text()
            .trim();
        }
        // Materials
        const materials = [];
        $cheerioProductPage(
          "dl.detail-list.js-detail-list.js-materials dd"
        ).each((index, element) => {
          materials.push($(element).text().trim());
        });
        // Country of origin
        const countryOfOrigin = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Country of Origin")'
        )
          .next("dd")
          .text()
          .trim();

        // Period
        const period = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Period")'
        )
          .next("dd")
          .text()
          .trim();
        // Item type
        const itemType = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Item Type")'
        )
          .next("dd")
          .text()
          .trim();
        // Color
        const color = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Color")'
        )
          .next("dd")
          .text()
          .trim();
        // Styled After
        const styledAfter = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Styled After")'
        )
          .next("dd")
          .text()
          .trim();
        // Bed Size
        const bedSize = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Bed Size")'
        )
          .next("dd")
          .text()
          .trim();
        // Table Height
        const tableHeight = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Table Height")'
        )
          .next("dd")
          .text()
          .trim();

        // Styles
        const styles = [];
        $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Styles")'
        )
          .nextAll("dd")
          .each((index, element) => {
            const style = $(element).find("a").text().trim();
            styles.push(style);
          });
        // Condition notes
        const conditionNotes = $cheerioProductPage(
          "dl.detail-list.js-detail-list dd span:first-child"
        )
          .text()
          .trim();

        // Condition
        const condition = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Condition")'
        )
          .next("dd")
          .text()
          .trim();

        // Number of seats
        const numberOfSeats = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Number of Seats")'
        )
          .next("dd")
          .text()
          .trim();
        // Seat height
        const seatHeight = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Seat Height")'
        )
          .next("dd")
          .text()
          .trim();
        // Table shape
        const tableShape = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Table Shape")'
        )
          .next("dd")
          .text()
          .trim();
        // Lamp shade
        const lampShade = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Lamp Shade")'
        )
          .next("dd")
          .text()
          .trim();
        // Designer
        const designer = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Designer")'
        )
          .next("dd")
          .text()
          .trim();
        // Artist
        const artist = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Artist")'
        )
          .next("dd")
          .text()
          .trim();
        // Power sources
        const powerSources = [];
        $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Power Sources")'
        )
          .nextAll("dd")
          .each((index, element) => {
            const powerSource = $(element).text().trim();
            powerSources.push(powerSource);
          });
        // Arm height
        const armHeight = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Arm Height")'
        )
          .next("dd")
          .text()
          .trim();
        // Pattern
        const pattern = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Pattern")'
        )
          .next("dd")
          .text()
          .trim();
        // Rug construction
        const rugConstruction = $cheerioProductPage(
          'dl.detail-list.js-detail-list dt:contains("Rug Construction")'
        )
          .next("dd")
          .text()
          .trim();

        let product = {
          url: link,
          id,
          title,
          description,
          price,
          retailPrice,
          images,
          category,
          brand,
          width,
          height,
          depth,
          location,
          sku: SKU ? SKU : id,
          materials,
          itemType,
          color,
          styledAfter,
          bedSize,
          tableHeight,
          armHeight,
          seatHeight,
          tableShape,
          numberOfSeats,
          designer,
          artist,
          pattern,
          styles,
          period,
          countryOfOrigin,
          conditionNotes,
          condition,
          lampShade,
          powerSources,
          rugConstruction,
        };
        products.push(product);
      }
    }

    return products;
  } catch (error) {
    console.log(error);
  }
};

let uploadAllChairishListings = async (mktModel) => {
  let mkt = await MktModel.findById(mktModel._id);

  try {
    let stores = await Store.find({ seller: mktModel.user });
    const user = await User.findById(mktModel.user);

    if (mkt.pastUploads.uploading) return;
    if (!mkt.storeUrl) return;
    if (stores?.length === 0) return;

    mkt.pastUploads.uploading = true;
    await mkt.save();

    emitSocketEvent("chairish-get-products-progress", {
      message: `Chairish upload started...`,
      user: user._id,
    });

    bulkUploadSlack(user, "Chairish");

    //Get listings
    emitSocketEvent("chairish-get-products-progress", {
      message: `Fetching listings, this may take a few minutes...`,
      user: user._id,
    });

    let listings = await chairishImportProducts(mkt.storeUrl);

    emitSocketEvent("chairish-get-products-progress", {
      message: `Saving listings on Kashew...`,
      user: user._id,
    });

    let removedListings = await RemovedListing.findOne({
      author: user._id,
    });

    for (let store of stores) {
      let sold = 0;
      let edit = 0;
      let errors = [];
      let savedProducts = [];
      let noChanges = 0;
      let priceReducedListings = [];

      let newProducts = [...listings];

      if (store.chairishLocation) {
        newProducts = newProducts.filter(
          (product) =>
            product.location?.trim()?.toLowerCase() ===
            store.chairishLocation?.trim()?.toLowerCase()
        );
      }
      if (newProducts?.length > 0) {
        let allListings = await Listing.find({
          author: user._id,
          store: store._id,
          $or: [{ status: "active" }, { status: "pending" }],
        }).select("SKU status");

        // First remove all listings not found
        for (let listing of allListings) {
          let found = await newProducts.find(
            (i) =>
              i.sku?.trim() == listing.SKU?.trim() ||
              i.id?.trim() == listing.SKU?.trim()
          );
          if (!found) {
            listing.status = "sold";
            await listing.save();
            sold++;
          }
        }

        allListings = await Listing.find({
          author: user._id,
          store: store._id,
        });

        // First make sure that there are no active duplicates and that products are not added if they axist already but are sold
        for (let product of newProducts) {
          let allFinds = allListings.filter(
            (i) =>
              i.SKU?.trim() == product.sku?.trim() ||
              i.SKU?.trim() == product.id?.trim()
          );

          if (allFinds.length > 0) {
            let found;

            if (allFinds.length === 1) {
              found = allFinds[0];
            } else if (allFinds.length > 1) {
              let actives = allFinds.filter((i) => i.status === "active");
              let pendings = allFinds.filter((i) => i.status === "pending");
              let solds = allFinds.filter((i) => i.status === "sold");
              let holds = allFinds.filter((i) => i.status === "hold");
              let notActives = allFinds.filter(
                (i) =>
                  i.status !== "pending" &&
                  i.status !== "active" &&
                  i.status !== "hold" &&
                  i.status !== "sold" &&
                  i.status !== "active-delivery" &&
                  i.status !== "active-pickup" &&
                  i.status !== "looking_for_carrier" &&
                  i.status !== "awaiting_shipping" &&
                  i.status !== "in_transit"
              );

              if (actives.length > 0) {
                found = actives[0];
              } else if (pendings.length > 0) {
                found = pendings[0];
              } else if (solds.length > 0) {
                found = solds[0];
              } else if (holds.length > 0) {
                found = holds[0];
              } else if (notActives.length > 0) {
                let newNotActive = [
                  ...notActives.sort(
                    (a, b) => moment(a.date).format() - moment(b.date).format()
                  ),
                ];
                found = newNotActive[0];
              }

              for (let find of allFinds) {
                if (
                  (find.status === "active" || found.status === "pending") &&
                  find._id !== found?._id
                ) {
                  find.status = "sold";
                  await find.save();
                  sold++;
                }
              }

              if (!found) continue;
            }
            if (found.status === "active") {
              let changes = compareCSVListing(product, found, "chairish");

              if (!Object.keys(changes).length > 0) {
                noChanges++;
                continue;
              }
            }

            if (product.price < found.price) {
              priceReducedListings.push(found._id);
            }

            found.price = product.price;
            found.store = store._id;
            found.estRetailPrice = product.retailPrice;
            found.uploadPrice = product.price;
            found.chairishId = product.id;
            found.SKU = product.sku;
            found.lastUpdated = moment();
            found.status =
              found.status === "pending"
                ? "pending"
                : found.status === "hold"
                ? "hold"
                : "active";
            found.title = decodeEntities(product.title);
            found.extraInfo = product.description
              ? csvDescriptionReplacements(decodeEntities(product.description))
              : "";
            found.expiration = moment().add(30, "days");
            if (product.tags) found.tags = product.tags;
            if (product.materials) found.materials = product.materials;
            found.quantity = product.quantity ? product.quantity : 1;
            found.freeShipping = found.title
              ?.toLowerCase()
              ?.includes("free shipping")
              ? true
              : false;
            if (product.height) {
              found.measurements.H = product.height;
            }
            if (product.depth) {
              found.measurements.D = product.depth;
            }
            if (product.width) {
              found.measurements.L = product.width;
            }
            if (product.materials?.length > 0) {
              found.materials = product.materials;
            }
            if (product.color) {
              found.colors = [product.color];
            }
            if (product.brand) {
              found.brand = product.brand;
            }
            if (product.styles?.length > 0) {
              found.styles = product.styles;
            }
            if (product.bedSize) {
              found.bedSize = product.bedSize;
            }
            if (product.tableHeight) {
              found.tableHeight = parseFloat(
                product.tableHeight?.replace(" in", "")
              );
            }
            if (product.armHeight) {
              found.armHeight = parseFloat(
                product.armHeight?.replace(" in", "")
              );
            }
            if (product.seatHeight) {
              found.seatHeight = parseFloat(
                product.seatHeight?.replace(" in", "")
              );
            }
            if (product.tableShape) {
              found.tableShape = product.tableShape;
            }
            if (product.numberOfSeats) {
              found.numberOfSeats = product.numberOfSeats;
            }
            if (product.designer) {
              found.designer = product.designer;
            }
            if (product.artist) {
              found.artist = product.artist;
            }
            if (product.pattern) {
              found.pattern = product.pattern;
            }
            if (product.period) {
              found.period = product.period;
            }
            if (product.countryOfOrigin) {
              found.countryOfOrigin = product.countryOfOrigin;
            }
            try {
              await found.save();
              edit++;
            } catch (err) {
              console.log(err);
              errors.push({ listing: found._id, error: err });
            }
          } else {
            if (removedListings) {
              let thisSKU = product.sku ? product.sku : product.id;

              if (thisSKU) {
                if (typeof thisSKU === "string") {
                  let skuFound = removedListings.SKUs.find(
                    (i) => i.trim() == thisSKU
                  );
                  if (skuFound) continue;
                } else if (typeof thisSKU === "number") {
                  let skuFound = removedListings.SKUs.find((i) => i == thisSKU);
                  if (skuFound) continue;
                }
              }
            }

            let itemInfo = await getNewSchema(
              decodeEntities(product.title),
              csvDescriptionReplacements(decodeEntities(product.description)),
              null
            );

            await new Promise((resolve) => setTimeout(resolve, 500));

            if (itemInfo) {
              let newListing = {
                price: product.price,
                chairishId: product.id,
                SKU: product.sku ? product.sku : product.id,
                status: "pending",
                brand: product.brand ? product.brand : "",
                newSchema: itemInfo,
                store: store._id,
                title: decodeEntities(product.title),
                freeShipping: product.title
                  ?.toLowerCase()
                  ?.includes("free shipping")
                  ? true
                  : false,
                extraInfo: product.description
                  ? csvDescriptionReplacements(
                      decodeEntities(product.description)
                    )
                  : "",
                delivery: {
                  coordinates: store.locationInfo.coordinates,
                  address: store.locationInfo.address,
                  stairs: store.locationInfo.stairs,
                  elevator: store.locationInfo.elevator,
                  flights: store.locationInfo.flights,
                  otherInfo: store.locationInfo.otherInfo,
                  phone: store.phone,
                  location: store.locationInfo.location,
                  item: itemInfo?.item,
                  vehicle: itemInfo?.vehicle,
                  helpers: itemInfo?.helpers,
                },
                commission: 80,
                expiration: moment().add(30, "days"),
                tags: product.tags?.length > 0 ? product.tags : [],
                materials:
                  product.materials?.length > 0 ? product.materials : [],
                quantity: product.quantity ? product.quantity : 1,
                condition: "Good",
                author: user._id,
                weight: product.item_weight ? product.item_weight : "",
                measurements: {
                  H: product.height ? product.height : "",
                  L: product.width ? product.width : "",
                  D: product.depth ? product.depth : "",
                },
                images: product.images,
                inProcess: true,
                lastUpdated: moment(),
                estRetailPrice: product.retailPrice ? product.retailPrice : "",
                colors: product.color ? [product.color] : [],
                styles: product.styles ? product.styles : [],
                bedSize: product.bedSize ? product.bedSize : "",
                tableHeight: product.tableHeight
                  ? parseFloat(product.tableHeight?.replace(" in", ""))
                  : "",
                armHeight: product.armHeight
                  ? parseFloat(product.armHeight?.replace(" in", ""))
                  : "",
                seatHeight: product.seatHeight
                  ? parseFloat(product.seatHeight?.replace(" in", ""))
                  : "",
                tableShape: product.tableShape ? product.tableShape : "",
                numberOfSeats: product.numberOfSeats
                  ? product.numberOfSeats
                  : "",
                designer: product.designer ? product.designer : "",
                artist: product.artist ? product.artist : "",
                pattern: product.pattern ? product.pattern : "",
                period: product.period ? product.period : "",
                countryOfOrigin: product.countryOfOrigin
                  ? product.countryOfOrigin
                  : "",
              };

              try {
                let list = await createUniqueListing(newListing);
                await list.save();
                savedProducts.push(list._id);
              } catch (err) {
                console.log(err);
                errors.push({ listing: product.sku, error: err });
              }
            } else {
              errors.push({
                listing: product.sku,
                error: "No category found",
              });
            }
          }
        }

        if (priceReducedListings?.length > 0)
          await notifyOfPriceChange(priceReducedListings);

        console.log({
          soldProducts: sold,
          editedProducts: edit,
          noChanges,
          errors,
          savedProducts: savedProducts?.length,
          date: moment(),
          store: store._id,
          storeName: store.name,
        });

        try {
          mkt.pastUploads.uploads = [
            ...mkt.pastUploads.uploads,
            {
              soldProducts: sold,
              editedProducts: edit,
              noChanges,
              errors,
              savedProducts,
              date: moment(),
            },
          ];
        } catch (err) {
          console.log(err);
        }

        if (savedProducts.length > 0) {
          await processNewListing(savedProducts);
        }
      }
    }

    mkt.pastUploads.uploading = false;
    await mkt.save();

    emitSocketEvent("chairish-get-products-end", {
      message: `Upload completed.`,
      user: user._id,
    });

    await Listing.updateMany(
      {
        author: user._id,
        $or: [{ status: "active" }, { status: "pending" }],
      },
      {
        $set: {
          expiration: new Date(
            new Date().getTime() + 30 * 24 * 60 * 60 * 1000
          ).toISOString(),
        },
      }
    ).catch((err) => {
      console.error("Error updating listings Expiration:", err);
      errorBugSlack(
        err,
        author._id,
        "Error updating listings Expiration date inside csvUpdate"
      );
    });

    await updateListingsStore(user._id);

    return "success";
  } catch (err) {
    console.log(err);

    mkt.pastUploads.uploading = false;
    await mkt.save();

    errorBugSlack({ error: err, route: "uploadAllChairishListings" });
  }
};

module.exports = {
  uploadAllChairishListings,
};
