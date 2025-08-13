# %% [markdown]
# PROYECTO FINAL AMAZON_PRODUCTOS_DATASETS

# %% [markdown]
# 1. Carga de los archivos

# %%
import pandas as pd ##importamos pandas como "pd"
import numpy as np ##importamos numpy como "np"

# %%
pip install openpyxl ##indicamos esto para abrir archivos excel

# %%
productos_general = pd.read_excel('c:\\Users\\jbartolomej\\Desktop\\Especialización\\Data\\PROYECTO FINAL\\Archivos en bruto\\amazon_products.xlsx',sheet_name="amazon_products") ##primer archivp
categorias_general = pd.read_csv('c:\\Users\\jbartolomej\\Desktop\\Especialización\\Data\\PROYECTO FINAL\\Archivos en bruto\\amazon_categories.csv')##segundo archivo
productos_general_copia = productos_general.copy()##hacemos una copia del primer archivo
categorias_general_copia = categorias_general.copy()##hacemos una copia del segundo archivo
pd.set_option('display.max_columns',None)

# %% [markdown]
# 2. Limpieza de datos y análisis general

# %%
categorias_general.info()## solo 2 columnas: la de ID de categoria de enteros, y el nombre de texto. Ambas columnas tienen 248 filas.
categorias_general.isnull().sum()##no tiene valores nulos
categorias_general.duplicated().sum()##no tiene duplicados
categorias_general.describe().T
categorias_general["id"].count() ##248 Ids asociados a nombres de categorías
categorias_general["category_name"].count() ##248 nombres de categoria
productos_general["category_id"].isnull().sum()##hay 456 productos que no tienen categoria del archivo de productos

# %%
categorias_general.rename(columns={"id":"category_id"},inplace=True)##poemos el mismo nombre que en el otro archivo

# %%
def convertir_int(valor): ##para que no haya errores al hacer el merge, hacemos una función para que el tipo de dato de ambas columnas sea igual
    if pd.isnull(valor): ##que no haga nada con los nulos
        return valor
    else:
        return int(valor) ##para los demás, que los pase a enteros

productos_general["category_id"] = productos_general["category_id"].apply(convertir_int).astype("Int64")##aplicamos el tipo Int64, para considerar los nulos
categorias_general["category_id"].dtypes## la columna del id del archivo de categorias ya es de tipo "Int64"

# %%
productos_categorias = productos_general.merge(categorias_general,how="left",on="category_id")## hacemos el merge como unión por la izquierda


# %%
columna_nombre_cateogria = productos_categorias.pop('category_name') ##elimnamos la columna del final, y la guardamos en esta variable
productos_categorias.insert(9, 'category_name', columna_nombre_cateogria) ##insertamos la columna, con el mismo nombre, depués de category ID

# %%
productos_categorias.rename(columns={"asin":"Product_id"},inplace=True) ##actualizamos nombre para mejor comprensión
productos_categorias.rename(columns={"price":"Final_price"},inplace=True) ##actualizamos nombre para mejor comprensión
productos_categorias.rename(columns={"listPrice":"Original_price"},inplace=True) ##actualizamos nombre para mejor comprensión 

# %%
productos_categorias.info() ## hay 199.999 productos
productos_categorias.isnull().sum() ## en algunas columnas, hay 465 valores nulos, y en la de mes más comprado 4685.
productos_categorias ["Product_id"].duplicated().sum() ## No hay códigos únicos de productos duplicados
productos_categorias ["title"].duplicated().sum() ## Hay títulos de productos duplicados. Consideramos que, aunque el título sea el mismo, el producto es distinto.

# %%
nulos_stars = productos_categorias[productos_categorias['stars'].isnull()] ##hacemos una columna con los nulos de la columna "stars"
nulos_stars.info() ## los 465 valores nulos coinciden en varias columnas, por lo que crearemos una nueva sin tener en cuenta esos prodcutos

# %%
productos_categoria_v1 = productos_categorias.dropna(subset=['stars'])## creamos nuevo DF, eliminando los nulos coincidentes de varias columnas

# %%
productos_categoria_v1.info() ## Todo igual, pero ahora con un DF de 199534 filas
productos_categoria_v1.duplicated().sum() ##el nuevo DF no tiene duplicados, como el anterior
productos_categoria_v1.isnull().sum() ## Solo la columna "month most bought" tiene nulos, uns 4220
productos_categoria_v1 ["Product_id"].duplicated().sum() ## otra manera de comprobar que no hay códigos de productos duplicados

# %%
productos_categoria_v1.describe().T ## de esta tabla se sacan conclusiones según diferentes análisis (reviews, estrellas y precio)

# %%
##Análisis por estrellas
productos_categoria_v1[productos_categoria_v1["stars"] == 5.0].shape[0] ## creamos un DF que filtre por 5 estrellas, y que nos devuelva una tupla solo con el primer elemento (filas)
productos_categoria_v1[productos_categoria_v1["stars"] == 5.0]["stars"].count() ## otra forma de sacar los 12070 productos 5 estrellas
productos_categoria_v1[productos_categoria_v1["stars"] == 0.0]["stars"].count() ## lo mismo pero para productos con 0 estrellasº

# %%
## Analisis por reviews
productos_categoria_v1[productos_categoria_v1["reviews"] == 0.0]["reviews"].count() ##61.378 productos no tienen reviews
productos_categoria_v1[productos_categoria_v1["reviews"] > 1000.0]["reviews"].count() ##24.221 productos tienen mas de 1000 reviews
productos_categoria_v1[productos_categoria_v1["reviews"] > 50000.0]["reviews"].count() ## 132 productos tienen más de 50.000 reviews
reviews_filtrado = productos_categoria_v1[(productos_categoria_v1["reviews"] > 0.0) & (productos_categoria_v1['reviews'] < 1000.0)] ## vamos a hacer una media con productos con mas de o reviews y menos de 1000
reviews_filtrado ["Product_id"].count() ## la nueva media se hará con 114.000 productos aproximadamente, para calcularla más aproximada.
reviews_filtrado ["reviews"].mean() ## media de 180 aproximademente, de los productos que tienen al menos 1 review, y menos de 1000.
reviews_filtrado ["reviews"].std() ## la desviación típica sigue siendo muy alta
reviews_filtrado.describe().T ## del tercer cuartil, al máximo, las reviews van de 254 a 999

# %%
## hay un error en la columna de "Original_price", que cuando el producto no tiene descuento, aparece 0.0 como su precio original
def correguir_precio_original (df):
    df["Original_price"] = df.apply(lambda row: row["Final_price"] if row["Original_price"] ==0.0 else row["Original_price"],axis=1)
    return df

correguir_precio_original(productos_categoria_v1)
## he creado una función que si aparece 0.0 en la columna de precio original, copia el precio final, y sino no hace nada.

# %%
## Análisis por precio
productos_categoria_v1[productos_categoria_v1["Final_price"] == 0.0]["Final_price"].count() ##hay 5299 productos que no tienen precio
productos_categoria_v1[productos_categoria_v1["Final_price"] >= 1000.0]["Final_price"].count() ## solo hay 211 productos que cuestan más de 1000€

# %%
productos_categoria_v1["reviews"] = productos_categoria_v1["reviews"].apply(lambda x:int(x)).astype("Int64")
productos_categoria_v1["boughtInLastYear"] = productos_categoria_v1["boughtInLastYear"].apply(lambda x:int(x)).astype("Int64")
## cambiamos la tipologia de dos columnas a números enteros para mayor precisión y claridad en los datos

# %%
## Queremos cambiar la forma en la que la columna de "mes más comprado" visualiza los meses, para mayor claridad
def convertir_nombre_mes (mes):
    if pd.isna(mes):
        return mes
    if mes == "01 - JAN":
        return "January"
    elif mes == "02 - FEB":
        return "February"
    elif mes == "03 - MAR":
        return "March"
    elif mes == "04 - APR":
        return "April"
    elif mes == "05 - MAY":
        return "May"
    elif mes == "06 - JUN":
        return "June"
    elif mes == "07 - JUL":
        return "July"
    elif mes == "08 - AUG":
        return "August"
    elif mes == "09 - SEP":
        return "September"
    elif mes == "10 - OCT":
        return "October"
    elif mes == "11 - NOV":
        return "November"
    elif mes == "12 - DEC":
        return "December" 

productos_categoria_v1["Month most bought"] = productos_categoria_v1["Month most bought"].apply(convertir_nombre_mes)     


# %%
def stars_category (stars):##categorizamos la cantidad de estrellas
    if pd.isna(stars): ## si da nulo, seuirá dando nulo
        return stars    
    try:
        stars = float(stars) ##si por lo que sea no es float devolverá valor no válido
    except ValueError:
        return "Not valid value"

    if stars == 0.0:
        return "Unrated"
    elif stars > 0.0 and stars <= 3.9:
        return "Poorly rated"
    elif stars >= 4.0 and stars <= 4.5:
        return "Medium level rated"
    elif stars >= 4.6 and stars <= 5.0:
        return "Highly rated"
    else:
        return "Value out of range" 
    
productos_categoria_v1.insert(5,"Stars_categorization",productos_categoria_v1["stars"].apply(stars_category)) ## insertamos la columna justo después 


# %%
def reviews_category (reviews):##categorizamos la cantidad de reviews
    if pd.isna(reviews): ## si da nulo, seuirá dando nulo
        return reviews    
    try:
        reviews = int(reviews) ##si por lo que sea no es int devolverá valor no válido
    except ValueError:
        return "Not valid value" 

    if reviews == 0:
        return "No reviews"
    elif reviews > 0 and reviews <= 20:
        return "few reviews"
    elif reviews >= 21 and reviews <= 200:
        return "Medium level of reviews"
    elif reviews >= 201 and reviews <= 1000:
        return "Several reviews"
    elif reviews >= 1001:
        return "Significant number of reviews"
    else:
        return "Value out of range" 
    
productos_categoria_v1.insert(7,"Reviews_categorization",productos_categoria_v1["reviews"].apply(reviews_category)) ## creamos la columna despúes de la columna "reviews"

# %%
def top_product(fila): ## definimos una función que indique que productos han sido muy valorados y con muchas reviews
    if fila['Stars_categorization'] == "Highly rated" and fila['Reviews_categorization'] == "Significant number of reviews":
        return "top product"
    else:
        return "not a top product"

productos_categoria_v1["Top_product"] = productos_categoria_v1.apply(top_product,axis=1) ## inserto la columna en el DF
Top_product_columna = productos_categoria_v1.pop("Top_product") ## la elimino del DF y me la guardo en una variable
productos_categoria_v1.insert(8,"Top_product",Top_product_columna) ## la inserto, a través de la variable en la posición deseada.
(productos_categoria_v1["Top_product"] == "top product").value_counts() ## Hay 11817 top products

# %%
def price_category (price):##categorizamos el precio
    if pd.isna(price): ## si da nulo, seuirá dando nulo
        return price    
    try:
        price = float(price) ##si por lo que sea no es float devolverá valor no válido
    except ValueError:
        return "Not valid value"

    if price == 0.0:
        return "No price"
    elif price > 0.0 and price <= 20.0:
        return "Very cheap" 
    elif price > 20.0 and price <= 50:
        return "Cheap"
    elif price > 50.0 and price <= 200.0:
        return "Medium"
    elif price > 200.0 and price <=2000.0:
        return "Expensive"
    else:
        return "Very expensive"

productos_categoria_v1.insert(10,"Price_categorization",productos_categoria_v1["Final_price"].apply(price_category)) ## se inserta en la columna de después del precio final


# %%
## creamos una columna que nos diga si el prodcuto tiene o no descuento, haciend que indique que no lo tiene si ambas columnas coinciden
productos_categoria_v1["Discount_status"] = productos_categoria_v1.apply(lambda fila: ("Product without discount" if fila ["Final_price"] == fila ["Original_price"] else "Product more expensive than before" if fila ["Final_price"] > fila["Original_price"] else "Product with discount"),axis=1)

# %%
Discount_status_columna = productos_categoria_v1.pop("Discount_status") ## la elimino del DF y me la guardo en una variable
productos_categoria_v1.insert(9,"Discount_status",Discount_status_columna) ## la insertamos en la posición deseada

# %%
## Insertamos el descuento real, con una formula de resta simple, y el método insert
productos_categoria_v1.insert(12,"Discount",productos_categoria_v1["Original_price"] - productos_categoria_v1["Final_price"])


# %%
## Queremos hacer lo mismo, pero con una columna que nos indique el porcentaje de descuento aplicado al producto
productos_categoria_v1["Discount_percentage"] = productos_categoria_v1.apply(lambda columna: ((columna["Original_price"]-columna["Final_price"])/columna["Original_price"])*100 if columna["Original_price"]!=0 else 0,axis=1)


# %%
Discount_percentage_columna = productos_categoria_v1.pop("Discount_percentage") ## la elimino del DF y me la guardo en una variable
productos_categoria_v1.insert(12,"Discount_percentage",Discount_percentage_columna) ## inserto la columna en la posición deseada

# %%
def purchasing_volume (volume):## categorizamos el volumen de compra de los productos
    if pd.isna(volume): ## si da nulo, seguirá dando nulo
        return volume    
    try:
        volume = int(volume) ## si por lo que sea no es entero devolverá valor no válido
    except ValueError:
        return "Not valid value"

    if volume < 0:
        return "Not valid value"
    elif volume == 0:
        return "Not purchased"
    elif volume > 0 and volume <= 75:
        return "Very low purchase volume" 
    elif volume > 75 and volume <= 200:
        return "Low purchase volume"
    elif volume > 200 and volume <= 400:
        return "Medium purchase volume"
    elif volume > 400 and volume <=1000: 
        return "High purchase volume"
    elif volume > 1000:
        return "Very high purchase volume"

productos_categoria_v1.insert(19,"Purchase_volume_categorization",productos_categoria_v1["boughtInLastYear"].apply(purchasing_volume)) ## se inserta en la columna de después de volumen de compra
    

# %%
## Por último, queremos saber el beneficio generado por producto
productos_categoria_v1.insert(20,"Anual_product_profit",productos_categoria_v1["boughtInLastYear"] * productos_categoria_v1["Final_price"]) 

# %% [markdown]
# 3. Análisis por lugar de fabricación del producto (Manufacture location)

# %%
conteo_localización = productos_categoria_v1.groupby("Manufacture location")["Product_id"].count().reset_index()
conteo_localización ["percentage"] = (conteo_localización["Product_id"]/conteo_localización ["Product_id"].sum())*100
conteo_localización ## En Europa se fabrica el 36 % de los productos, en Asia y Norteamérica, el 22 % cada uno, en Sudamérica, el 9 %, y en Oceanía y África, aproximadamente el 4 % cada uno.

# %%
manufa_stars_catego = productos_categoria_v1.pivot_table(index="Manufacture location", columns= "Stars_categorization",values="Product_id", aggfunc = "count")
manufa_stars_catego.insert(4,"Total",manufa_stars_catego["Highly rated"] + manufa_stars_catego["Medium level rated"]+ manufa_stars_catego["Poorly rated"] + manufa_stars_catego["Unrated"])
manufa_stars_catego.insert(1,"perecntage_Highly",manufa_stars_catego["Highly rated"]/manufa_stars_catego["Total"]*100)
manufa_stars_catego.insert(5,"percentage_unrated",manufa_stars_catego["Unrated"]/manufa_stars_catego["Total"]*100)
manufa_stars_catego.insert(4,"percentage_poorly",manufa_stars_catego["Poorly rated"]/manufa_stars_catego["Total"]*100)
manufa_stars_catego
## Igualmente, la cantidad de productos por categoría de estrellas es muy similar. 
## En proporción, África lidera la categoría “Hihgly rated” y también la de “poorly rated” indicando que sus productos o gustan mucho o no gustan nada. 
## Sudamérica lidera la categoría de productos “unrated”. 

# %%
media_stars_localización = productos_categoria_v1.groupby("Manufacture location")["stars"].mean().reset_index()
media_stars_localización ## La media de estrellas por lugar de fabricación es muy equitativa, siendo ligeramente inferior la de los productos fabricados en Sudamérica.

# %%
productos_categoria_v1.groupby("Manufacture location")["reviews"].mean().reset_index()
## los productos de Norte américa son los prodcutos que de media tienen más reviews, y los que menos los fabricados en África 

# %%
top_prod_manuf = productos_categoria_v1.groupby("Manufacture location")["Top_product"].apply(lambda x: (x == "top product").sum()).reset_index() 
Total_top = productos_categoria_v1.groupby("Manufacture location")["Product_id"].count().reset_index()
top_prod_manuf.insert(2,"Total",Total_top["Product_id"])
top_prod_manuf.insert(3,"perecntage top prodcut",top_prod_manuf["Top_product"]/top_prod_manuf["Total"]*100)
top_prod_manuf
## El porcentaje de "top prodcuts" más alto está en Oceanía, con un 6,18 % y el más bajo en Europa y Sudamérica, con un 5,83 %. Asia y Norte América tienen un buen porcentaje, comparado con la cantidad total de productos.

# %%
productos_categoria_v1.pivot_table(index="Manufacture location", columns= "Price_categorization",values="Product_id", aggfunc = "count")
## En Asia se fabrican casi la misma cantidad de productos de la categoría "Very expensive" que en Europa, teniendo Europa muchos más productos.
## En Sudamerica se fabrican pocos productos de categoría "Very expensive", incluso menos que en Oceania, que tiene un volumen de fabricación menor de productos

# %%
productos_categoria_v1.groupby("Manufacture location")["Final_price"].mean().reset_index()
## De media, los productos con mayor precio se hacen en Oceanía, y con menor precio en Sudamérica.

# %%
Total_productos_continente = productos_categoria_v1.groupby("Manufacture location") ["Discount_status"].count() ## variable con el total de productos por continente
con_descuento = productos_categoria_v1[productos_categoria_v1['Discount_status'] == 'Product with discount'] ## variable filtrada con productos con descuento
descuento_por_continente = con_descuento.groupby("Manufacture location")["Discount_status"].count() ## contamos los productos que tienen descuento por contienente
porcentaje_descuento = (descuento_por_continente / Total_productos_continente) * 100 ## lo indicamos en procentaje
print (porcentaje_descuento) 
## Norte américa es el continente que tiene el porcentaje mayor de productos con descuento, y Oceanía y Europa los que menor porcentaje tienen.


# %%
Locaclizacion_beneficio = productos_categoria_v1.groupby("Manufacture location")["Anual_product_profit"].mean().reset_index()
Locaclizacion_beneficio
## La rentabilidad media por producto según lugar de fabricación es similar en todos los continentes, exceptuando Norte América, que destaca por su baja rentabilidad respecto al resto.

# %%
conteo = productos_categoria_v1.groupby(['Manufacture location', 'category_name']).size().reset_index(name='cantidad')
conteo_ordenado = conteo.sort_values(['Manufacture location', 'cantidad'], ascending=[True, False])
top2_por_continente = conteo_ordenado.groupby('Manufacture location').head(2)
top2_por_continente ## la categoría más fabricada en cada continente es "Ropa de mujer", excepto en Asía que es "Ropa de hombre". No obstante, las dos cateogiras de prodcto más fabricadas en todos los continentes se asocian a productos de moda.

# %%
loca_cate_profit = productos_categoria_v1.groupby(['Manufacture location', 'category_name'])['Anual_product_profit'].mean().reset_index() ## agrupar por continente y categoria, y calcular el beneficio medio
ordenado = loca_cate_profit.sort_values(["Manufacture location", "Anual_product_profit"],ascending=[True,False]) ## Ordenar por continenete y beenficio medio descendente
ordenado.groupby("Manufacture location").head(2) ## agrupar por continente, y solo obtener las dos categorias con beneficio medio más alto
## Las categorias cuyos prodcutos han dado un mayor beneficio anual según el contienente de fabricación son: Maletas de viaje, Monitores de ordeandores, muebles para niños y jueguetes de barcos para niños.


# %% [markdown]
# 4. Análisis por estrellas y reviews (Stars y Reviews)

# %%
productos_categoria_v1.groupby("Stars_categorization")["Product_id"].count().reset_index()
## la mayoria de productos tienen una valoración media o alta

# %%
productos_categoria_v1.groupby("Stars_categorization")["Final_price"].mean().reset_index().sort_values(by="Final_price", ascending=False)
## los prodcutos "mejor valorados" ("hihgly rated") son los que tienen el precio medio más bajo. Sin embargo, los peor valorados o no valorados, tienen el precio medio más alto
productos_categoria_v1.groupby("Reviews_categorization")["Final_price"].mean().reset_index().sort_values(by="Final_price")
## Los productos con más reviews son los que menor precio medio tienen. Los que tienen el precio medio más alto son los que tienen pocas o ninguna review.

# %%
productos_categoria_v1[(productos_categoria_v1["Top_product"]== "top product")]["Top_product"].value_counts()
productos_categoria_v1[(productos_categoria_v1["Top_product"]== "top product") & (productos_categoria_v1["Discount_status"] == "Product with discount")]["Top_product"].value_counts()
## Hay 11.817 Top products. De esos, 4.810 tienen algun descuento.

# %%
descuento_estrellass = productos_categoria_v1.groupby("Stars_categorization")["Discount"].mean().reset_index()
precio_estrellas = productos_categoria_v1.groupby("Stars_categorization")["Final_price"].mean().reset_index()
analisis_estrellas = pd.merge(descuento_estrellass, precio_estrellas, on="Stars_categorization")
analisis_estrellas
## lo más valorados son los que menos descuento tienen, pero también son ya los más baratos. Los no valorados tienen muy poco descuento

# %%
productos_categoria_v1.groupby("category_name")["stars"].mean().reset_index().sort_values(by="stars",ascending=False).head(5)
## las 5 categorías de producto mejor valoradas son: Aspiradoras y cuidado de suelo, herramientas de automoción, productos de pelo, televisiones y productos de video, y videojuegos.
productos_categoria_v1.groupby("category_name")["stars"].mean().reset_index().sort_values(by="stars",ascending=False).tail(5)
## las 5 categorías por producto peor valoradas son: Productos de maternidad, muebles para niños, asistentes de voz, materiales industriales y juguetes de barco para niños.

# %%
productos_categoria_v1.groupby("category_name")["reviews"].mean().reset_index().sort_values(by="reviews",ascending=False).head(5)
## Las cinco categorías más comentadas son: Casas inteligentes, productos de peluquería, asistentes de voz para casas inteligentes, videojuegos, productos de relajación y bienestar.
productos_categoria_v1.groupby("category_name")["reviews"].mean().reset_index().sort_values(by="reviews",ascending=False)
## hay cinco categorías que cuyos productos no sumnan ninguna review. Llama la atención que tres de ellas están asociadas a moda de hombre, cuando es una categoria muy demandada.

# %%
productos_categoria_v1.groupby("Purchase_volume_categorization")["reviews"].mean().reset_index().sort_values(by="reviews",ascending=False)
## El volumen de compra de un producto está relacionado con la cantidad de reviews que recibe
productos_categoria_v1.groupby("Purchase_volume_categorization")["stars"].mean().reset_index().sort_values(by="stars",ascending=False)
## El volumen de compra de un producto no está relacionado con el nivel de valoraciones que recibe. Puede que las valoraciones de un producto no tengan capacidad de influencia en la decisión de compra del cliente

# %%
profit_stars = productos_categoria_v1.groupby("Stars_categorization")["Anual_product_profit"].mean().reset_index().sort_values(by="Anual_product_profit",ascending=False)
count_stars = productos_categoria_v1.groupby("Stars_categorization")["Product_id"].count().reset_index()
stars_profit_count = profit_stars.merge(count_stars,how="left",on="Stars_categorization")
stars_mean = productos_categoria_v1.groupby("Stars_categorization")["Final_price"].mean().reset_index()
stars_profit_count_mean = stars_profit_count.merge(stars_mean,how="left",on="Stars_categorization")
stars_profit_count_mean
## el beneficio anual de un producto no se ve afectado por el número de estrellas que tenga. Los consumidores no se influencian por la valoración del producto.

# %%
productos_categoria_v1.pivot_table(index="Reviews_categorization", columns= "Month most bought",values="Product_id", aggfunc = "count")
## los productos con más reviews, son más comprados en los meses de agosto y navidad. Generalmente todos los productos son más comprados en estos meses. Los productos sin reviews son muy comprados en Agosto.
productos_categoria_v1.pivot_table(index="Stars_categorization", columns= "Month most bought",values="Product_id", aggfunc = "count")
## lo mismo pasa con los productos con más estrellas

# %% [markdown]
# 5. Análisis por precio y decuento

# %%
productos_ordenados_precio = productos_categoria_v1.sort_values(by='Final_price', ascending=False)
productos_ordenados_precio.iloc[0] ## El producto más caro vale 19.400€ y se llama "Replicas Marinas"
productos_ordenados_descuento = productos_categoria_v1.sort_values(by='Discount', ascending=False)
productos_ordenados_descuento.iloc[0] ## El producto con más decuento es de 680.99€ y se llama "bObsweep PetHair SLAM Robot Vacuum Cleaner"
productos_categoria_v1["Discount"].mean() ## El descuento medio de cada producto es de 4€ de descuento
productos_categoria_v1["Final_price"].mean() ## El precio medio de cada producto es de 50€ 

# %%
productos_categoria_v1.groupby("Top_product")[["Final_price","Discount"]].mean().reset_index()
## Los productos TOP tienen un precio medio más bajo y un descuento medio mayor que los productos normales 
productos_categoria_v1.groupby("isBestSeller")[["Final_price","Discount"]].mean().reset_index()
## Los productos Best seller también son ,ás baratos y tienen más descuento que los demás

# %%
precio_cat = productos_categoria_v1.groupby("Price_categorization")[["Final_price","Discount"]].mean().reset_index().sort_values(by="Final_price",ascending=False)
count_cat = productos_categoria_v1.groupby("Price_categorization")["Product_id"].count().reset_index()
definitivo = precio_cat.merge(count_cat,how="left",on="Price_categorization")
definitivo
## Hay 59 productos en la cateogría de "Muy caros", que tiene un precio medio de 3.670€, y ningun producto tiene descuento
## Quitando la categoria de "Very expensive", de media, cuanto más caro es el prodcuto, mayor descuento tiene
## Hay 5299 productos de los que no se dispone de su precio
## La categoria en la que hay más productos es la de "Very cheap" (76.432) 


# %%
Discount_cat = productos_categoria_v1.groupby("Discount_status")["Final_price"].mean().reset_index().sort_values(by="Final_price",ascending=False)
Dis_count = productos_categoria_v1.groupby("Discount_status")["Product_id"].count().reset_index()
defi_descuento = Discount_cat.merge(Dis_count,how="left",on="Discount_status")
defi_descuento.insert(3,"Porcentaje del total", defi_descuento["Product_id"]/defi_descuento["Product_id"].sum()*100)
defi_descuento
## El precio medio de los productos con descuento y sin descuent es muy similar (49€)
## Solo hay 53.531 productos co descuento, es decir, solo el 26% de los productos.
## Hay 136 productos cuyo precio final es más caro que el precio original. Su precio medio es de 36€

# %%
resumen_categoria_precios = productos_categoria_v1.groupby("category_name")[["Final_price", "Discount"]].mean()
top_3_precio = resumen_categoria_precios.sort_values(by='Final_price', ascending=False).head(3)
top_3_precio ## Las 3 categoría con el precio medio más caro son: Monitores de ordenador, Maletas y Sistemas de seguridad para viviendas
bottom_precio = resumen_categoria_precios.sort_values(by='Final_price', ascending=False).tail(3)
bottom_precio ## Las 3 categorías con el precio medio más bajo son: Relojes de chico, juegutes de recién nacido y bombillas
top_3_discount = resumen_categoria_precios.sort_values(by='Discount', ascending=False).head(3)
top_3_discount ## De las tres categorías con el precio medio más alto, solo Maletas no figura entre las de mayor descuento, siendo reemplazada por Zapatos de hombre
bottom_discount = resumen_categoria_precios.sort_values(by='Discount', ascending=False).tail(3)
bottom_discount ## Las tres cateogrías con menos descuento medio son: Juegetes de barcos para niños, Materiales industriales y adornos para telas
## Es calro que la tendencia es a myor precio, mayor descuento


# %%
productos_categoria_v1.groupby('Purchase_volume_categorization')[["Final_price", "Discount"]].mean().reset_index().sort_values(by="Final_price",ascending=False)
## Los productos con alto volumen de compra, tienen un precio medio levemente superior a los productos con menos volumen
productos_categoria_v1.groupby('Purchase_volume_categorization')[["Final_price", "Discount"]].mean().reset_index().sort_values(by="Discount",ascending=False)
## Los productos que no han sido comprados nunca, son los que tienen un descuento medio más bajo. 

volumen_precio = productos_categoria_v1.pivot_table(index="Purchase_volume_categorization", columns= "Price_categorization",values="Product_id", aggfunc = "count")
count_volumen = productos_categoria_v1.groupby("Purchase_volume_categorization")["Product_id"].count().reset_index()
defi_volu_precio = volumen_precio.merge(count_volumen,how="left",on= "Purchase_volume_categorization")
defi_volu_precio
## Los productos muy baratos dominan todas las categorias, especialmente las de bajo volumen de compra  
## La categoria "very hihg purchase volume", tiene la mayor cantidad de productos caros porcentualmente, lo que indica que el precio no frena el volumen de compra
## los productos con precio medio destacan en la categoría de productos no comprados, por lo que precios intermedios no incentivan la compra
 

# %%
profit_price_cat = productos_categoria_v1.groupby("Price_categorization")["Anual_product_profit"].mean().reset_index().sort_values(by="Anual_product_profit",ascending=False)
count_price_cat = productos_categoria_v1.groupby("Price_categorization")["Product_id"].count().reset_index()
defi_prof_price_cat = profit_price_cat.merge(count_price_cat,how="left",on="Price_categorization")
defi_prof_price_cat
## Cuanto más caro es el producto, mayor beneficio anual ofrece. Los compradores no son sensibles a precios altos.
## La cateogria de producto muy caro, lidera el beneficio anual, unicamente contando con 59 productos.
top_3_products = productos_categoria_v1[productos_categoria_v1["Price_categorization"] == "Very expensive"].sort_values(by="Anual_product_profit",ascending=False).head(3)[["title","Final_price","boughtInLastYear","Anual_product_profit"]]
top_3_products
## El beneficio anual de los 3 mejores productos ha sido de 83 MM, 31 MM y 24 MM. El que ha dado 83 MM se llama "Tektini", se ha vendido 20.000 veces a un precio de 4.198,99€ 

# %%
profit_dis_cat = productos_categoria_v1.groupby("Discount_status")["Anual_product_profit"].mean().reset_index().sort_values(by="Anual_product_profit",ascending=False)
count_dis_cat = productos_categoria_v1.groupby("Discount_status")["Product_id"].count().reset_index()
defi_prof_dis_cat = profit_dis_cat.merge(count_dis_cat,how="left",on="Discount_status")
defi_prof_dis_cat.insert(3,"Porcentaje del total", defi_prof_dis_cat["Anual_product_profit"]/defi_prof_dis_cat["Anual_product_profit"].sum()*100)
defi_prof_dis_cat.insert(3,"Porcentaje del total_cuenta", defi_prof_dis_cat["Product_id"]/defi_prof_dis_cat["Product_id"].sum()*100)
defi_prof_dis_cat
## Los productos sin descuento representan el 73%, mientras que su beneficio medio anual casi el 40%. En cambio, los productos con descuento son el 26%, y representan el 35% del beneficio anual. Son más renatbles los productos con descuento
## Es sorprendente que en solo 136 (0,06%) productos su precio final era más alto que el original, y represnetan el 25% de renatabilidad

# %% [markdown]
# 6. Análisis por categoria

# %%
productos_categoria_v1["category_id"].nunique() ## Tenemos 35 categorías de producto
conteo_cat = productos_categoria_v1.groupby("category_name")["Product_id"].count().reset_index().sort_values(by="Product_id",ascending=False)
conteo_cat.head(3) ## Las tres categorias que más productos tienen son: Ropa de hombre, Ropa de mujer y Zapatos de hombre
conteo_cat.tail(3) ## Las tres categorias que menos productos tienen son: Jueguetes de barcos para niños, Sistemas de seguridad en casas, asistentes de voz en casas

# %%
Best_S_cat = productos_categoria_v1.groupby("category_name")["isBestSeller"].sum().reset_index().sort_values(by="isBestSeller",ascending=False)
Best_S_cat.head(3) ## Las tres categorías que más Best sellers tienen son: Equipo de automoción, Ropa de hombre y Juguetes
Best_S_cat.tail(4) ## Hay tres categorías que no tienen ningún Best Seller: Maletas, asistentes de voz en casas y Jueguetes de barcos para niños. Relojes de niño tiene 1
top_product_cat = productos_categoria_v1[productos_categoria_v1["Top_product"] == "top product"].groupby("category_name")["Top_product"].count().reset_index().sort_values(by="Top_product",ascending=False)
top_product_cat.head(3) ## Las tres categorias con más productos top son: Ropa de chica, juguetes y juegos y televisiones
top_product_cat.tail(3) ## las tres categorias que menos top product tienen son: Relojes de niño asistentes de voz para casas y juguetes de barco para niños

# %%
volumen_categoria = productos_categoria_v1.groupby("category_name")["boughtInLastYear"].mean().reset_index().sort_values(by="boughtInLastYear",ascending=False)
volumen_categoria.head(3) ## Las 3 categorias más demandadas fueron: Videoconsolas, Monitores de ordenador y Juguetes de barco para niños
volumen_categoria.tail(3) ## Las tres cateogrías menos demandadas fueron: Jueguetes de deporte y exteriores, y equipo de automoción
profit_categoria = productos_categoria_v1.groupby("category_name")["Anual_product_profit"].mean().reset_index().sort_values(by="Anual_product_profit",ascending=False)
profit_categoria.head(3) ## Las tres categorias con mayor beneficio medio anual son: Monitores de ordenador, Juegutes de niños para barcos y Maletas
profit_categoria.tail(3) ## las tres categorías con menor beneficio medio anual son: Juguetes de deporte y exteriores, jueguetes de recién nacidos y productos de relajación y bienestar


# %% [markdown]
# 7. Análisis sobre volumen de compra

# %%
count_volum = productos_categoria_v1.groupby("Purchase_volume_categorization")["Product_id"].count().reset_index().sort_values(by="Product_id",ascending=False)
count_volum.insert(2,"Porcentaje del total_cuenta", count_volum["Product_id"]/count_volum["Product_id"].sum()*100)
profit_volum = productos_categoria_v1.groupby("Purchase_volume_categorization")["Anual_product_profit"].mean().reset_index()
count_volum_v1 = count_volum.merge(profit_volum,how="left",on="Purchase_volume_categorization")
count_volum_v1.insert(4,"Porcentaje del total_beneficio", count_volum_v1["Anual_product_profit"]/count_volum_v1["Anual_product_profit"].sum()*100)
count_volum_v1
## "Very high purchase volume" representa solo el 15,45% de las cuentas, pero genera un 87% del beneficio total. Una minoría de productos o clientes genera la mayoría del beneficio
## Las categorías de volumen de compra con más productos: "High purchase volume", "Low" y "Very low”, suman el 68% de productos, pero solo un 9,4% del beneficio total. Hay muchos productos o clientes con bajo impacto económico
## El grupo "Not purchased" no aporta beneficio y representa un 2,11% del total de productos. Esos productos se deben reactivar o eliminar
## Las categorías de "low y very low purchase volume", acaparan muchos productos y no tienen casi impacto en el beneficio anual. Habría que establecer una nueva estrategia para estos productos

# %% [markdown]
# 8. Análisis sobre el mes con mayor volumen de compras

# %%
count_mes = productos_categoria_v1.groupby("Month most bought")["Product_id"].count().reset_index().sort_values(by="Product_id",ascending=False) 
count_mes.insert(2,"Porcentaje del total_cuenta",count_mes["Product_id"]/count_mes["Product_id"].sum()*100)
profit_mes = productos_categoria_v1.groupby("Month most bought")["Anual_product_profit"].mean().reset_index()
count_mes_v1 = count_mes.merge(profit_mes,how="left",on="Month most bought")
count_mes_v1.insert(4,"Porcentaje del total_beneficio", count_mes_v1["Anual_product_profit"]/count_mes_v1["Anual_product_profit"].sum()*100)
count_mes_v1
## Los meses de mayor demanda de productos y beneficio son los cercanos a navidad y verano 
## El mes que más beneficio anual ofrece es diciembre, con un beneficio medio de 84.780€ 
## Agosto es el mes con más demanda de productos, pero no el más rentable, por lo que el volumen no siempre se traduce en mayor beneficio
## Meses como septiembre, octubre y abril tienen menor volumen y beneficio, lo que podría indicar baja actividad

# %%
productos_categoria_v1["Month most bought"] = productos_categoria_v1["Month most bought"].fillna("Unknown") ## rellenamos los nulos de la única columna que tiene para evitar errores al exportar

# %%
productos_categoria_v1.to_excel("poductos_categoria_v1.xlsx",index=False) ## Lo exportamos a excel para hacer la visualización a traves de Power BI


