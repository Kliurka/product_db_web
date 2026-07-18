from .dashboard import dashboard


from .products import (
    product_add,
    product_detail,
    product_edit,
    product_list,
    product_qr,
    scan_qr,
)

from .orders import (
    order_add,
    order_detail,
    order_edit,
    order_list,
)

from .customers import (
    customer_add,
    customer_edit,
    customer_list,
    customer_detail,
)

from .storage import (
    storage_list,
    storage_detail,
    storage_add,
    storage_edit,
)

from .textures import (
    texture_list,
    texture_detail,
    texture_add,
    texture_edit,
)

from .users import (
    user_add,
    user_edit,
    user_list,
)


from .product_images import (
    product_image_add,
    product_image_delete,
)

from .auth import (
    login_view,
    logout_view,
)


from .product_types import (
    product_type_list,
    product_type_detail,
    product_type_add,
    product_type_edit,
)

from .discounts import (
    discount_list,
    discount_detail,
    discount_add,
    discount_edit,
)

from .taxes import (
    tax_list,
    tax_detail,
    tax_add,
    tax_edit,
)