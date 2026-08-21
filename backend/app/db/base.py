from app.db.base_class import Base

# Import ALL models here
from app.models.user import User
from app.models.medicine import Medicine
from app.models.batch import Batch
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.supplier import Supplier
from app.models.settings import Settings
from app.models.token import RefreshToken, BlockedToken
from app.models.activity_log import ActivityLog
from app.models.prescription import Prescription, PrescriptionItem
from app.models.permission import RolePermission
from app.models.currency import Currency