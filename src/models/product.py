# src/models/product.py

class Product:
    """Representasi Produk yang dijual."""
    def __init__(self, product_id: int, product_name: str, description: str, price: int):
        self.product_id = product_id
        self.product_name = product_name
        self.description = description
        self.price = price

    def __repr__(self):
        return f"Product(ID: {self.product_id}, Name: {self.product_name}, Price: {self.price})"