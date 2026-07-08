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
    order_edit,
    order_list,
)

from .customers import (
    customer_add,
    customer_edit,
    customer_list,
)

from .storage import (
    storage_add,
    storage_edit,
    storage_list,
)

from .textures import (
    texture_add,
    texture_edit,
    texture_list,
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