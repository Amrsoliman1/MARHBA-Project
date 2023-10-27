import streamlit as st
import base64
import pyodbc


# Connect to DB
__cnx = None

def marhba_connection():

    global __cnx
    server = 'localhost'  
    db = 'Project (Marhba)'

    if __cnx is None :
        __cnx = pyodbc.connect(driver='{SQL Server Native Client 11.0}', host=server, database=db,trusted_connection='yes')

    return __cnx

# Queries 
def get_categories():
    conn = marhba_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT category_id, category_name FROM Category')
    categories = cursor.fetchall()
    cursor.close()
    
    return categories

def get_subcategories(category_id):
    conn = marhba_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT subcategory_id, subcategory_name FROM Subcategory WHERE category_id = ?', category_id)
    subcategories = cursor.fetchall()
    cursor.close()
    
    return subcategories

def get_products(subcategory_id):
    products = []
    conn = marhba_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT product_name, unit_price FROM Product WHERE subcategory_id = ?', subcategory_id)
    for row in cursor:
        products.append((row.product_name, row.unit_price))
    return products

def get_Payment_methods():
    methods = []
    conn = marhba_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT payment_id , payment_method_name FROM payment_method ')
    for row in cursor:
        methods.append((row.payment_id,row.payment_method_name))
    return methods

def insert_new_order(order):
    conn = marhba_connection()
    cursor = conn.cursor()
    query = "INSERT INTO Orders (total_Price,payment_method_id) VALUES (?,?)"
    data = (order['Total Price'],order['Payment method id'])

    cursor.execute(query, data)
    conn.commit()

    
# App Code   

@st.experimental_memo
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img1 = get_img_as_base64(r"C:\Users\asa\Documents\Back.jpg")
img2 = get_img_as_base64(r"C:\Users\asa\Documents\Side.jpg")

page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/png;base64,{img1}");
    background-size: 100% 100%;
    background-position: top left;
    background-repeat: no-repeat;
    background-attachment: local;
    color: white;
    }}

    [data-testid="stSidebar"] > div:first-child {{
    background-image: url("data:image/png;base64,{img2}");

    background-size: 360px 100%;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: white;
    }}

    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    color: white;
    }}

    [data-testid="stToolbar"] {{
    right: 2rem;
    }}

    .available-products {{
        margin-top: 1rem;
        color: white;
    }}
    }}

    </style>
    """

st.markdown(page_bg_img, unsafe_allow_html=True)

st.sidebar.header("Welcome to our Market")
total_order_amount = 0
selected_payment_method = None
quantity = 0
category_options = get_categories()
with st.sidebar:
        selected_category = st.selectbox('Choose Category', category_options, format_func=lambda x: x[1])

if selected_category:
        subcategory_options = get_subcategories(selected_category[0])
        with st.sidebar:
            selected_subcategory = st.selectbox("Select a subcategory:", subcategory_options, format_func=lambda x: x[1])

        if selected_subcategory:
            products = get_products(selected_subcategory[0])
            st.markdown('<div class="available-products">', unsafe_allow_html=True)
            st.markdown('<div style="color: white; font-size: 3em; margin-bottom: 1rem;">Available Products</div>', unsafe_allow_html=True)

            for product in products:
                product_name, price = product
                quantity = st.number_input(f"{product_name} (Price: ${price}):", min_value=0, value=0)
                if quantity > 0:
                    product_total = quantity * int(price)
                    st.write(f"Ordered {quantity} {product_name} for a total of ${product_total}")
                    total_order_amount += product_total

            

payment_methods = get_Payment_methods()
selected_payment_method = st.selectbox('Choose Payment Method', payment_methods, format_func=lambda x: x[1])
st.subheader(f"Total Order Amount: ${total_order_amount}")


if st.button("Place Order"):
        
        order = {'Total Price': total_order_amount,'Payment method id' : selected_payment_method[0]}
        # Insert the order into the database
        insert_new_order(order)
        st.success(f"Order submitted with {selected_payment_method[1]}")
        st.success(f"Total Order Amount: ${total_order_amount}")

if st.button("Make Another Order"):
        # Reset Order Amount and Payment Method for a new order
        total_order_amount = 0
        selected_payment_method = None


