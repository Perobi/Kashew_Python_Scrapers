from selenium import webdriver 
from selenium.webdriver.support.ui import Select

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import re
import csv

from selenium.webdriver.common.by import By
import pandas as pd 


driver = webdriver.Chrome()  # Initialize the webdriver outside of the loop


links = ["https://www.etsy.com/listing/1328614479/",
"https://www.etsy.com/listing/1391695459/",
"https://www.etsy.com/listing/1343383033/",
"https://www.etsy.com/listing/1481336476/",
"https://www.etsy.com/listing/1339851770/",
"https://www.etsy.com/listing/1504517171/",
"https://www.etsy.com/listing/1233739816/",
"https://www.etsy.com/listing/1501610775/",
"https://www.etsy.com/listing/1475297399/",
"https://www.etsy.com/listing/1488867972/",
"https://www.etsy.com/listing/1351015743/",
"https://www.etsy.com/listing/1398401215/",
"https://www.etsy.com/listing/1474430267/",
"https://www.etsy.com/listing/1487969746/",
"https://www.etsy.com/listing/1306689188/",
"https://www.etsy.com/listing/1380009650/",
"https://www.etsy.com/listing/1472720661/",
"https://www.etsy.com/listing/1472167083/",
"https://www.etsy.com/listing/1425509762/",
"https://www.etsy.com/listing/1476334361/",
"https://www.etsy.com/listing/1272366310/",
"https://www.etsy.com/listing/1353439455/",
"https://www.etsy.com/listing/1233423011/",
"https://www.etsy.com/listing/1472078283/",
"https://www.etsy.com/listing/1245347788/",
"https://www.etsy.com/listing/1493062206/",
"https://www.etsy.com/listing/1480928664/",
"https://www.etsy.com/listing/1495016221/",
"https://www.etsy.com/listing/1294387003/",
"https://www.etsy.com/listing/1451654254/",
"https://www.etsy.com/listing/1255383266/",
"https://www.etsy.com/listing/1259553404/",
"https://www.etsy.com/listing/1491377238/",
"https://www.etsy.com/listing/1299320593/",
"https://www.etsy.com/listing/1267700688/",
"https://www.etsy.com/listing/1259918182/",
"https://www.etsy.com/listing/1488504736/",
"https://www.etsy.com/listing/1451752290/",
"https://www.etsy.com/listing/1290962416/",
"https://www.etsy.com/listing/1502192345/",
"https://www.etsy.com/listing/1462702866/",
"https://www.etsy.com/listing/1260075026/",
"https://www.etsy.com/listing/1502996687/",
"https://www.etsy.com/listing/1490438398/",
"https://www.etsy.com/listing/1495031545/",
"https://www.etsy.com/listing/1467589544/",
"https://www.etsy.com/listing/1470675859/",
"https://www.etsy.com/listing/1473741453/",
"https://www.etsy.com/listing/1336759446/",
"https://www.etsy.com/listing/1509914141/",
"https://www.etsy.com/listing/1494206972/",
"https://www.etsy.com/listing/1504607003",
"https://www.etsy.com/listing/1280075606/",
"https://www.etsy.com/listing/1451282470/",
"https://www.etsy.com/listing/1511073483/",
"https://www.etsy.com/listing/1510738679/",
"https://www.etsy.com/listing/1487699674/",
"https://www.etsy.com/listing/1495312885/",
"https://www.etsy.com/listing/1350899465/",
"https://www.etsy.com/listing/1467579304/",
"https://www.etsy.com/listing/1480781653/",
"https://www.etsy.com/listing/1450743674/",
"https://www.etsy.com/listing/1464128297/",
"https://www.etsy.com/listing/1259965374/",
"https://www.etsy.com/listing/1496587550/",
"https://www.etsy.com/listing/1511031397/",
"https://www.etsy.com/listing/1499480631/",
"https://www.etsy.com/listing/1408033811/",
"https://www.etsy.com/listing/1478428378/",
"https://www.etsy.com/listing/1345632479/",
"https://www.etsy.com/listing/1502200459/",
"https://www.etsy.com/listing/1510963627/",
"https://www.etsy.com/listing/1496627770/",
"https://www.etsy.com/listing/1495379840/",
"https://www.etsy.com/listing/1502211387/",
"https://www.etsy.com/listing/1500580269/",
"https://www.etsy.com/listing/1312832153/",
"https://www.etsy.com/listing/1289153876/",
"https://www.etsy.com/listing/1447974928/",
"https://www.etsy.com/listing/1354843855/",
"https://www.etsy.com/listing/1343365377/",
"https://www.etsy.com/listing/1486462354/",
"https://www.etsy.com/listing/1486366764/",
"https://www.etsy.com/listing/1282108311/",
"https://www.etsy.com/listing/1268108752/",
"https://www.etsy.com/listing/1267650106/",
"https://www.etsy.com/listing/1473020827/",
"https://www.etsy.com/listing/1506947177/",
"https://www.etsy.com/listing/1502228485/",
"https://www.etsy.com/listing/1292180210/",
"https://www.etsy.com/listing/1478696285/",
"https://www.etsy.com/listing/1473769791/",
"https://www.etsy.com/listing/1410939601/",
"https://www.etsy.com/listing/1455854670/",
"https://www.etsy.com/listing/1465887239/",
"https://www.etsy.com/listing/1396726984/",
"https://www.etsy.com/listing/1494405554/",
"https://www.etsy.com/listing/1458609212/",
"https://www.etsy.com/listing/1451291586/",
"https://www.etsy.com/listing/1497190612/",
"https://www.etsy.com/listing/1506377735/",
"https://www.etsy.com/listing/1291063492/vintage-bamboo-queen-headboard-with?click_key=7872ff1dbf7e3a66baee0240a89d4014b3993cbf%3A1291063492&click_sum=c8a9a03b&ref=shop_home_active_119",
"https://www.etsy.com/listing/1492644598/queen-post-headboard-by-american-of?click_key=bebca94c67f4f8337950e3a2ca5d26d371d9aa37%3A1492644598&click_sum=b97df56d&ref=shop_home_active_120",
"https://www.etsy.com/listing/1476204415/french-provincial-dresser-with-12?click_key=b4b68ad76a6a489d36cdeaaac382908b8c42b3a8%3A1476204415&click_sum=cf1995fb&ref=shop_home_active_122&cns=1",
"https://www.etsy.com/listing/1452101050/rattan-dresser-project-by-dixie-wicker?click_key=4b9b01552e7d1aa1877e76bc73e1afdc6f86ba1a%3A1452101050&click_sum=bca62491&ref=shop_home_active_123&cns=1",
"https://www.etsy.com/listing/1511431345/vintage-french-country-nightstands-pair?click_key=f8a7fc786f0dc37c9d86a96604a70be77cbef4a5%3A1511431345&click_sum=a81b36f8&ref=shop_home_active_124&frs=1",
"https://www.etsy.com/listing/1507169719/provincial-king-headboard-with-burl-wood?click_key=2ed64fd9a54b0213fcd428548b3d1983379e8363%3A1507169719&click_sum=e0010a32&ref=shop_home_active_125",
"https://www.etsy.com/listing/1208821637/vintage-rattan-nightstands-free-shipping?click_key=b79b638891f903c869fee29daf9519e1363bf4da%3A1208821637&click_sum=3deeb06c&ref=shop_home_active_127&frs=1",
"https://www.etsy.com/listing/1497201004/bamboo-nesting-tables-free-shipping-set?click_key=09456a4c0ae0280d7ef5f616dfd1c49aead31700%3A1497201004&click_sum=3dcc80ad&ref=shop_home_active_128&frs=1",
"https://www.etsy.com/listing/1510839689/set-of-2-rattan-mirrors-51x23-free?click_key=f5ed93983db76537a3baf612afe4568f0f99d6be%3A1510839689&click_sum=9742bcba&ref=shop_home_active_129&frs=1",
"https://www.etsy.com/listing/1508599463/mahogany-secretary-desk-with-ball-and?click_key=60f5ae6add8847d7bffa21023a4bd168e86c5af2%3A1508599463&click_sum=1f88043d&ref=shop_home_active_130",
"https://www.etsy.com/listing/1492892700/midcentury-modern-highboard-credenza?click_key=cd82a9d3b909867d065b35e52b6c455915e18ed8%3A1492892700&click_sum=b5407233&ref=shop_home_active_131",
"https://www.etsy.com/listing/1491583882/french-provincial-queen-headboard?click_key=dc06bdb7d90c8d962e0dad6dce22f521bbe48772%3A1491583882&click_sum=a0c4efeb&ref=shop_home_active_132&cns=1",
"https://www.etsy.com/listing/1473224473/vintage-chinoiserie-entry-table-by?click_key=8cb00dd08dd25ec069adb283176f27151beed6d6%3A1473224473&click_sum=2dfa5f2e&ref=shop_home_active_133&cns=1",
"https://www.etsy.com/listing/1287324413/pencil-reed-console-table-with-waterfall?click_key=08f81f0905ba3be7acfab3391adc74eb77b736c0%3A1287324413&click_sum=895ce7de&ref=shop_home_active_134&cns=1",
"https://www.etsy.com/listing/1358511847/faux-bamboo-rattan-queen-headboard?click_key=904faa29412b67ff91d2b677879d19fc14306eb8%3A1358511847&click_sum=610542c9&ref=shop_home_active_135",
"https://www.etsy.com/listing/1337109064/rattan-full-headboards-pair-set-of-2?click_key=78f2b9b3d5f9053e65f1175089f53a284c299d96%3A1337109064&click_sum=e2ebdad1&ref=shop_home_active_136",
"https://www.etsy.com/listing/1456590738/faux-bamboo-desk-by-thomasville-allegro?click_key=087432f0db7e5fcd819f589b97438c011fd68edb%3A1456590738&click_sum=10c8f603&ref=shop_home_active_138",
"https://www.etsy.com/listing/1451283786/faux-bamboo-desk-by-henry-link-bali-hai?click_key=bccfa555f2156f0371cdc240f5c441561c3bc9fc%3A1451283786&click_sum=ab3be93c&ref=shop_home_active_139&cns=1",
"https://www.etsy.com/listing/1467315712/vintage-pencil-reed-server-by-american?click_key=51ca9cf2ed3bda1cca9cdf3ec31c93af2ed621c5%3A1467315712&click_sum=28ec69b5&ref=shop_home_active_142",
"https://www.etsy.com/listing/1497223338/french-provincial-queen-headboard-by?click_key=6ce166694b9b6a47d0f855647cf9f47df889c4b4%3A1497223338&click_sum=be1daad3&ref=shop_home_active_144",
"https://www.etsy.com/listing/1411044671/set-of-2-pink-swivel-club-chairs-vintage?click_key=1aef1650641dca0fe805b61b9e46912742d5c13a%3A1411044671&click_sum=4aa5c2c8&ref=shop_home_active_145&cns=1",
"https://www.etsy.com/listing/1396561284/vintage-faux-bamboo-tallboy-dresser?click_key=884521016afe832481beab4db83f09ae01e54b46%3A1396561284&click_sum=9204682f&ref=shop_home_active_146",
"https://www.etsy.com/listing/1466261480/vintage-twin-wicker-headboards-set-of-2?click_key=fdacd79439ab249e84b8cc28fd45c359f7d12d2a%3A1466261480&click_sum=97f6abb7&ref=shop_home_active_148&cns=1",
"https://www.etsy.com/listing/1476113129/vintage-faux-bamboo-tallboy-dresser?click_key=f1ce9e14c2c7a0fc45da1466329a69f61eaceee4%3A1476113129&click_sum=f04b1b60&ref=shop_home_active_149",
"https://www.etsy.com/listing/1462068399/rattan-armoire-dresser-project-by-dixie?click_key=056e0c07a7e7c1c56a68c9eb9fd092a5075167c1%3A1462068399&click_sum=76201358&ref=shop_home_active_150&crt=1",
"https://www.etsy.com/listing/1455297131/vintage-faux-bamboo-armoire-dresser?click_key=38aba235ff107bebd40927c405a325303ae92052%3A1455297131&click_sum=3f799d39&ref=shop_home_active_151",
"https://www.etsy.com/listing/1254759784/thomasville-allegro-nightstand-free?click_key=1a81ca083a85db7c901a99f815e82e0ebe58f991%3A1254759784&click_sum=2401da93&ref=shop_home_active_152&frs=1",
"https://www.etsy.com/listing/1257661372/vintage-twin-headboards-by-henry-link?click_key=ec029172ec58d85d6d5b7a3fabd1fb69a44e7c73%3A1257661372&click_sum=de052604&ref=shop_home_active_153",
"https://www.etsy.com/listing/1510489323/rare-henry-link-vanity-table-with-faux?click_key=d66edc9ac008543dca7adb92d2dc228e34c55c6d%3A1510489323&click_sum=120a962b&ref=shop_home_active_154",
"https://www.etsy.com/listing/1495693706/unique-fretwork-king-headboard-with?click_key=14023665f71243272985c3f05a1a9c408f4777cb%3A1495693706&click_sum=6851a3c3&ref=shop_home_active_155",
"https://www.etsy.com/listing/1507138909/set-of-2-french-country-arm-chairs-by?click_key=fab1d2b7c5c7c1e3d35583c30d33e35ad01f4846%3A1507138909&click_sum=2805cb8d&ref=shop_home_active_156",
"https://www.etsy.com/listing/1488807646/vintage-faux-bamboo-tallboy-dresser?click_key=caedd450dbded792526fda8c14f0adc13c9184c9%3A1488807646&click_sum=030d8e2a&ref=shop_home_active_157",
"https://www.etsy.com/listing/1320756195/vintage-henry-link-wicker-server-cabinet?click_key=55677ed3cb4df9cf3e5c2facd5e3e6530ab2e768%3A1320756195&click_sum=0b2b1f49&ref=shop_home_active_158",
"https://www.etsy.com/listing/1411010841/henry-link-bali-hai-nightstand-free?click_key=db4b26115b821d957e2b8dd440e93267424416a1%3A1411010841&click_sum=da70d0ee&ref=shop_home_active_159&frs=1",
"https://www.etsy.com/listing/1457762684/set-of-2-henry-link-mirrors-45x19-free?click_key=d3a24cda7e71f45e1a8b897d2fbea97c6927b61e%3A1457762684&click_sum=e84dc4af&ref=shop_home_active_160&frs=1",
"https://www.etsy.com/listing/1457744452/set-of-2-henry-link-mirrors-45x19-free?click_key=0affb41ba2746b476108c93e7e61b95380262cc9%3A1457744452&click_sum=a6b2de52&ref=shop_home_active_161&frs=1",
"https://www.etsy.com/listing/1460785597/vintage-twin-headboards-set-of-2-white?click_key=05f234a8d328e968200dae7d559178a536984468%3A1460785597&click_sum=d40f1638&ref=shop_home_active_163",
"https://www.etsy.com/listing/1101537971/faux-bamboo-nightstand-free-shipping-one?click_key=59592291acfa7295d94d656668c1b8eabed1ade3%3A1101537971&click_sum=ea5c5ea8&ref=shop_home_active_165&frs=1",
"https://www.etsy.com/listing/1507097513/vintage-faux-bamboo-cabinet-42w-15d-30h?click_key=7af881e35369a5f55ba725b7c726b77492fb1daa%3A1507097513&click_sum=9acc53dc&ref=shop_home_active_166&cns=1",
"https://www.etsy.com/listing/1231073932/set-of-2-vintage-rattan-dining-chairs?click_key=33c24c48aebfaddddefa358bc60d1b186aa4b293%3A1231073932&click_sum=566be869&ref=shop_home_active_167",
"https://www.etsy.com/listing/1390821086/vintage-faux-bamboo-queen-headboard-by?click_key=62c56a6268d679d08f9ddfa45ac49fc74bf841a3%3A1390821086&click_sum=42030d06&ref=shop_home_active_168&cns=1",
"https://www.etsy.com/listing/1457806826/vintage-pencil-reed-half-moon-side-table?click_key=9bc5943f93c8e67ae53a4058c0607d20853b6376%3A1457806826&click_sum=d3541977&ref=shop_home_active_169&frs=1",
"https://www.etsy.com/listing/1446359112/set-of-2-wicker-twin-headboards-vintage?click_key=3dcddc77e0632417138f96922a5ea020bd1898a6%3A1446359112&click_sum=b6d9a34a&ref=shop_home_active_170&cns=1",
"https://www.etsy.com/listing/1256031984/set-of-2-vintage-barrel-chairs-with-faux?click_key=1bcf61ea5dbbf948e9f306587f26fbef1f1f89f8%3A1256031984&click_sum=eaa6576f&ref=shop_home_active_171&cns=1",
"https://www.etsy.com/listing/1500678903/white-rattan-king-headboard-by-dixie?click_key=3445eb43fecde4a125df9e6a60a413c2af120471%3A1500678903&click_sum=0eb71b88&ref=shop_home_active_172",
"https://www.etsy.com/listing/1486388374/faux-bamboo-desk-with-4-drawers-by?click_key=701e0675beb1194500658c73775946d51afc07a0%3A1486388374&click_sum=ffc8dd42&ref=shop_home_active_173",
"https://www.etsy.com/listing/1463932342/vintage-faux-bamboo-nightstand-28-wide?click_key=cadc1b41b782c86ef2fa56c12db2390eee4f9163%3A1463932342&click_sum=cb573abb&ref=shop_home_active_175&frs=1",
"https://www.etsy.com/listing/1356337192/vintage-faux-bamboo-nightstand-by-henry?click_key=6840f4fcf9e403591dab6da782116df1c76dbb3b%3A1356337192&click_sum=47517b7c&ref=shop_home_active_176&frs=1",
"https://www.etsy.com/listing/1488786900/faux-bamboo-nightstand-with-3-drawers-30?click_key=c2912dcae36aa821424482b6ccdc14d0a1bf9820%3A1488786900&click_sum=b691eed2&ref=shop_home_active_177",
"https://www.etsy.com/listing/1488777702/faux-bamboo-nightstand-with-3-drawers-30?click_key=be4a9ad9dd0356870fe876418cb19f54070a5517%3A1488777702&click_sum=c8c5f012&ref=shop_home_active_178",
"https://www.etsy.com/listing/1502829265/vintage-faux-bamboo-desk-creamy-white?click_key=256764c7d18648c5b04c3681e56de515d726c7dd%3A1502829265&click_sum=9720d913&ref=shop_home_active_179",
"https://www.etsy.com/listing/1488461394/vintage-faux-bamboo-desk-creamy-white?click_key=70ce34ef74b0249f027cc3c2bfcad577b1586213%3A1488461394&click_sum=1f7d32a1&ref=shop_home_active_180",
"https://www.etsy.com/listing/1245310881/vintage-rattan-end-table-free-shipping?click_key=12fe42a99230c48533c0c7986a7bef2fc9affff9%3A1245310881&click_sum=3066fc04&ref=shop_home_active_181&frs=1",
"https://www.etsy.com/listing/1467665588/vintage-chinese-carved-rosewood-plant?click_key=d80113902e67f65465e28817a3e7cc654bdf1aac%3A1467665588&click_sum=fe6b0766&ref=shop_home_active_183&frs=1&cns=1",
"https://www.etsy.com/listing/1286156819/drexel-accolade-mirror-48x33-free?click_key=f45c6de78ebf63be5bdac85397dcb27610ca23a6%3A1286156819&click_sum=4edf2012&ref=shop_home_active_185&frs=1",
"https://www.etsy.com/listing/1271565554/faux-bamboo-mirror-56x32-free-shipping?click_key=179340d3211f9f4fa4b7ddd2c0b01b1ef0cb4b0e%3A1271565554&click_sum=08ddc16f&ref=shop_home_active_186&frs=1",
"https://www.etsy.com/listing/1285722429/faux-bamboo-rattan-mirror-by-dixie-47x33?click_key=07f09eb2ac9368f28a88fdc85a87788bf46c5a29%3A1285722429&click_sum=12fe54f9&ref=shop_home_active_187&frs=1",
"https://www.etsy.com/listing/1460589525/vintage-trunk-with-bamboo-and-woven?click_key=530fea3d67bf789fb8633699073aa36511d8eae3%3A1460589525&click_sum=e90248a3&ref=shop_home_active_188&frs=1",
"https://www.etsy.com/listing/1261601590/vintage-rattan-dining-chair-free?click_key=62b880c73167329bb833d95489035a96721da26b%3A1261601590&click_sum=5c67234a&ref=shop_home_active_191&frs=1",
"https://www.etsy.com/listing/1510515339/vintage-square-coffee-table-by-lane?click_key=30a13e00db287bd327a2014b9fbaae3c5294ada6%3A1510515339&click_sum=1a6915ef&ref=shop_home_active_192",
"https://www.etsy.com/listing/1508641675/rattan-nightstand-by-dixie-wicker-weve?click_key=b9e9f54731dd89500ef81f7d2b6f554dcf3a2db3%3A1508641675&click_sum=09a4dfa9&ref=shop_home_active_193&frs=1",
"https://www.etsy.com/listing/1470408127/faux-bamboo-queen-headboard-with-rattan?click_key=e17ef5452b09bcbabf7410096f7ca748dad69aec%3A1470408127&click_sum=c763ad2d&ref=shop_home_active_200",]

data = { "sku": [], 'title':[], 'price':[], 'condition':[], 'width':[], 'height':[], 'depth':[], 'description':[], 'tags':[], 'images':[]}

for url in links: 
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(("xpath", '//div[@class="body-wrap wt-body-max-width wt-display-flex-md wt-flex-direction-column-xs"]')))

        # -------------------SKU-------------------
        sku = url.split("/")[4]
        data['sku'].append(sku)

        listing_container = driver.find_element("xpath",'//div[@class="body-wrap wt-body-max-width wt-display-flex-md wt-flex-direction-column-xs"]')

        # -------------------Listing Title-------------------
        try:
            data['title'].append(listing_container.find_element("xpath",'//h1[@data-buy-box-listing-title="true"]').text)
        except:
            data['title'].append("")

        # -------------------Listing Price-------------------
        try:
            price_element = listing_container.find_element("xpath",'//div[@data-buy-box-region="price"]')
            price_el = price_element.find_element("xpath",'//p[@class="wt-text-title-03 wt-mr-xs-1 "]').text
            currency_value = price_el.split("\n")[1][1:]
            data['price'].append(currency_value)
        except:
            data['price'].append("")

        # -------------------Listing Condition-------------------
        data['condition'].append("Excellent")

        # -------------------Listing Dimensions-------------------
        try:
            dimensions_box = listing_container.find_element("xpath",'//div[@class="wt-display-flex-xs"]')
            dimensions = dimensions_box.find_elements("xpath",'.//div[@class="wt-ml-xs-2"]')
            width, height, depth = "", "", ""
            for dim in dimensions:
                try:
                    dimension_name = dim.text.split(":")[0].strip().lower()
                    dimension_value = float(dim.text.split(":")[1].strip().split(" ")[0])
                
                    if dimension_name == 'width' or dimension_name == 'overall width':
                        width = dimension_value
                    elif dimension_name == 'height' or dimension_name == 'overall height':
                        height = dimension_value
                    elif dimension_name == 'depth' or dimension_name == 'overall depth':
                        depth = dimension_value
                except Exception as e:
                    print(f"Failed to process dimension: {dim.text}. Error: {str(e)}")
            data['width'].append(width)
            data['height'].append(height)
            data['depth'].append(depth)
        except:
            data['width'].append("")
            data['height'].append("")
            data['depth'].append("")

        # -------------------Listing Description-------------------
        try:
            description_box = listing_container.find_element("xpath",'//p[@data-product-details-description-text-content]')
            description_text = description_box.text

            # split the description into paragraphs
            paragraphs = description_text.split('\n')

            # create a list to store the paragraphs we want to keep
            description_filtered = []

            for paragraph in paragraphs:
                # remove the return policy
                if "RETURNS" in paragraph:
                    continue
                # remove paragraph with phone number
                if "You may also call or text me at" in paragraph:
                    continue
                if "call" in paragraph or "text" in paragraph or "Call" in paragraph or "Text" in paragraph or "239-560-200" in paragraph or "meet" in paragraph or "Fort Myers" in paragraph or "FREE" in paragraph:
                    continue
                # remove shipping info
                if "SHIPPING" in paragraph or "LOCAL PICKUP" in paragraph or "We can meet locally" in paragraph or "Shipping" in paragraph or "Cancellations" in paragraph or "returns" in paragraph or "I also have" in paragraph or "etsy" in paragraph:
                    continue
                # remove empty lines or lines only containing whitespace
                if paragraph.strip() == '':
                    continue
                # if none of the above conditions were met, add the paragraph to our list
                description_filtered.append(paragraph)

            # join the paragraphs back together into a single string
            description_final = "\n".join(description_filtered)

            # add to the descriptions list
            data['description'].append(description_final) # removing the trailing new line
        except:
            data['description'].append("")

        # -------------------Listing Tags-------------------
        try:
            tag_container = listing_container.find_element("xpath",'//p[@id="legacy-materials-product-details"]')
            tag_text = tag_container.text

            # Split the text at the colon and strip whitespace from the second part
            tag = tag_text.split(":")[1].strip()

            # Append to the tags list
            data['tags'].append(tag)
        except:
            data['tags'].append("")

        # -------------------Listing Images-------------------
        try:
            image_container = listing_container.find_element("xpath",'//div[@data-component="listing-page-image-carousel"]')
            image_elements = image_container.find_elements(By.TAG_NAME, 'img')
            image_links = []
            for image in image_elements:
                image_links.append(image.get_attribute('src')) 
            data['images'].append(image_links)
        except:
            data['images'].append([])

        print("done scraping listing title: ", data)
    except Exception as e:
        print(f"An error occurred on page: {url}. Error: {str(e)}. Skipping to next URL.")
        continue

# Once the loop is done, convert your dictionary into a pandas DataFrame
df = pd.DataFrame(data)

# Finally, write your DataFrame to a CSV file
df.to_csv('elle_woodworthy.csv', index=False)

driver.quit()