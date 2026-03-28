import pymongo
from pymongo.errors import ServerSelectionTimeoutError
import logging
import random
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fallback in-memory database if MongoDB is not running locally
_mock_sales = []
_mock_history = []


def _generate_seed_data():
    """Generate a rich, realistic seed dataset for demo purposes."""
    products = [
        {"item_id": "P001", "name": "Premium Coffee Beans",  "category": "Beverage",  "sales_qty": 320, "price": 14.99, "cost": 7.50, "supplier": "BeanCo",      "shelf_location": "A1"},
        {"item_id": "P002", "name": "Organic Almonds",       "category": "Snacks",    "sales_qty": 185, "price": 9.99,  "cost": 5.20, "supplier": "NutHouse",    "shelf_location": "B3"},
        {"item_id": "P003", "name": "Energy Drink (6-Pack)", "category": "Beverage",  "sales_qty": 540, "price": 8.49,  "cost": 3.80, "supplier": "VoltDrinks",  "shelf_location": "A2"},
        {"item_id": "P004", "name": "Dark Chocolate 72%",    "category": "Snacks",    "sales_qty": 250, "price": 5.49,  "cost": 2.10, "supplier": "CocoaPure",   "shelf_location": "B1"},
        {"item_id": "P005", "name": "Green Tea Matcha",      "category": "Beverage",  "sales_qty": 190, "price": 6.99,  "cost": 3.00, "supplier": "LeafBrew",    "shelf_location": "A3"},
        {"item_id": "P006", "name": "Protein Bar Variety",   "category": "Snacks",    "sales_qty": 410, "price": 3.99,  "cost": 1.60, "supplier": "FitFuel",     "shelf_location": "B2"},
        {"item_id": "P007", "name": "Fresh Orange Juice 1L", "category": "Beverage",  "sales_qty": 280, "price": 4.99,  "cost": 2.20, "supplier": "FreshSqz",    "shelf_location": "A4"},
        {"item_id": "P008", "name": "Granola Mix 500g",      "category": "Breakfast", "sales_qty": 165, "price": 7.49,  "cost": 3.50, "supplier": "MorningBite", "shelf_location": "C1"},
        {"item_id": "P009", "name": "Greek Yogurt Tub",      "category": "Dairy",     "sales_qty": 300, "price": 5.99,  "cost": 2.80, "supplier": "DairyFresh",  "shelf_location": "D1"},
        {"item_id": "P010", "name": "Sparkling Water 12-Pk", "category": "Beverage",  "sales_qty": 420, "price": 6.99,  "cost": 2.50, "supplier": "BubbleCo",    "shelf_location": "A5"},
        {"item_id": "P011", "name": "Trail Mix 400g",        "category": "Snacks",    "sales_qty": 200, "price": 6.49,  "cost": 2.90, "supplier": "NutHouse",    "shelf_location": "B4"},
        {"item_id": "P012", "name": "Whole Wheat Bread",     "category": "Bakery",    "sales_qty": 350, "price": 3.99,  "cost": 1.50, "supplier": "GoldenCrust", "shelf_location": "E1"},
        {"item_id": "P013", "name": "Organic Milk 2L",       "category": "Dairy",     "sales_qty": 270, "price": 5.49,  "cost": 2.60, "supplier": "DairyFresh",  "shelf_location": "D2"},
        {"item_id": "P014", "name": "Instant Oatmeal Box",   "category": "Breakfast", "sales_qty": 220, "price": 4.29,  "cost": 1.80, "supplier": "MorningBite", "shelf_location": "C2"},
        {"item_id": "P015", "name": "Peanut Butter Jar",     "category": "Snacks",    "sales_qty": 310, "price": 5.99,  "cost": 2.40, "supplier": "NutHouse",    "shelf_location": "B5"},
        {"item_id": "P016", "name": "Coconut Water 500ml",   "category": "Beverage",  "sales_qty": 175, "price": 3.49,  "cost": 1.30, "supplier": "TropiCo",     "shelf_location": "A6"},
        {"item_id": "P017", "name": "Cheese Crackers Pack",  "category": "Snacks",    "sales_qty": 290, "price": 4.49,  "cost": 1.70, "supplier": "CrunchTime",  "shelf_location": "B6"},
        {"item_id": "P018", "name": "Banana Chips 200g",     "category": "Snacks",    "sales_qty": 145, "price": 3.29,  "cost": 1.20, "supplier": "TropiCo",     "shelf_location": "B7"},
        {"item_id": "P019", "name": "Butter Croissant 4-Pk", "category": "Bakery",    "sales_qty": 180, "price": 5.99,  "cost": 2.50, "supplier": "GoldenCrust", "shelf_location": "E2"},
        {"item_id": "P020", "name": "Flavored Yogurt 6-Pk",  "category": "Dairy",     "sales_qty": 240, "price": 7.99,  "cost": 3.60, "supplier": "DairyFresh",  "shelf_location": "D3"},
    ]
    return products


def _generate_historical_data():
    """Generate 30-day simulated historical sales for trend analysis."""
    random.seed(42)  # Fixed seed for reproducible demo data
    history = []
    base_date = datetime(2024, 3, 1)  # Fixed base date so data is stable
    categories = ["Beverage", "Snacks", "Breakfast", "Dairy", "Bakery"]
    base_rev = {"Beverage": 850, "Snacks": 620, "Breakfast": 340, "Dairy": 480, "Bakery": 290}

    for day_offset in range(30):
        date = base_date + timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")
        for cat in categories:
            revenue = base_rev[cat] + (day_offset * random.uniform(2, 8)) + random.uniform(-50, 50)
            units = int(revenue / random.uniform(4, 8))
            history.append({
                "date": date_str,
                "category": cat,
                "daily_revenue": round(revenue, 2),
                "units_sold": units
            })
    return history


class Database:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="shelf_space_opt"):
        self.uri = uri
        self.db_name = db_name
        self.use_mock = False
        self.client = None
        self.db = None
        self._connect()

    def _connect(self):
        try:
            self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self.client.server_info()
            self.db = self.client[self.db_name]

            # Seed data into MongoDB if the collection is empty
            col = self.db["sales_data"]
            if col.count_documents({}) == 0:
                col.insert_many(_generate_seed_data())
                logger.info("Seeded MongoDB with initial product data.")

            hist_col = self.db["sales_history"]
            if hist_col.count_documents({}) == 0:
                hist_col.insert_many(_generate_historical_data())
                logger.info("Seeded MongoDB with historical trend data.")

            logger.info("Successfully connected to MongoDB.")
            self.use_mock = False
        except ServerSelectionTimeoutError:
            logger.warning("MongoDB not detected. Falling back to in-memory mock database.")
            self.use_mock = True
            self._seed_mock()

    def _seed_mock(self):
        global _mock_sales, _mock_history
        if not _mock_sales:
            _mock_sales.extend(_generate_seed_data())
        if not _mock_history:
            _mock_history.extend(_generate_historical_data())

    def get_connection_info(self):
        if self.use_mock:
            return {"type": "In-Memory Mock", "status": "active", "records": len(_mock_sales), "history_records": len(_mock_history)}
        else:
            count = self.db["sales_data"].count_documents({})
            return {"type": "MongoDB", "status": "connected", "uri": self.uri, "records": count}

    def insert_sales_data(self, data):
        if self.use_mock:
            if isinstance(data, list):
                _mock_sales.extend(data)
            else:
                _mock_sales.append(data)
            return {"status": "success", "inserted": True, "db_type": "mock"}
        else:
            col = self.db["sales_data"]
            if isinstance(data, list):
                col.insert_many(data)
            else:
                col.insert_one(data)
            return {"status": "success", "inserted": True, "db_type": "mongodb"}

    def get_all_sales(self):
        if self.use_mock:
            return list(_mock_sales)
        else:
            return list(self.db["sales_data"].find({}, {"_id": 0}))

    def get_historical_data(self):
        if self.use_mock:
            return list(_mock_history)
        else:
            return list(self.db["sales_history"].find({}, {"_id": 0}))

    def delete_product(self, item_id):
        if self.use_mock:
            global _mock_sales
            before = len(_mock_sales)
            _mock_sales = [p for p in _mock_sales if p.get("item_id") != item_id]
            return {"deleted": before - len(_mock_sales)}
        else:
            result = self.db["sales_data"].delete_many({"item_id": item_id})
            return {"deleted": result.deleted_count}

    def search_products(self, query):
        if self.use_mock:
            q = query.lower()
            return [p for p in _mock_sales
                    if q in p.get("name", "").lower()
                    or q in p.get("category", "").lower()
                    or q in p.get("item_id", "").lower()]
        else:
            return list(self.db["sales_data"].find({"$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}},
                {"item_id": {"$regex": query, "$options": "i"}}
            ]}, {"_id": 0}))


# Singleton
db = Database()
