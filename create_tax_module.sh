#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/home/bar/product_db_web"
VIEWS_DIR="$PROJECT_DIR/inventory/views"
TEMPLATES_DIR="$PROJECT_DIR/inventory/templates/inventory"

echo "Creating Taxes module from Discounts module..."

required_files=(
    "$VIEWS_DIR/discounts.py"
    "$TEMPLATES_DIR/discount_list.html"
    "$TEMPLATES_DIR/discount_detail.html"
    "$TEMPLATES_DIR/discount_form.html"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "ERROR: source file not found: $file"
        exit 1
    fi
done

target_files=(
    "$VIEWS_DIR/taxes.py"
    "$TEMPLATES_DIR/tax_list.html"
    "$TEMPLATES_DIR/tax_detail.html"
    "$TEMPLATES_DIR/tax_form.html"
)

for file in "${target_files[@]}"; do
    if [[ -e "$file" ]]; then
        echo "ERROR: target file already exists: $file"
        echo "Remove or rename it before running this script."
        exit 1
    fi
done

cp "$VIEWS_DIR/discounts.py" \
   "$VIEWS_DIR/taxes.py"

cp "$TEMPLATES_DIR/discount_list.html" \
   "$TEMPLATES_DIR/tax_list.html"

cp "$TEMPLATES_DIR/discount_detail.html" \
   "$TEMPLATES_DIR/tax_detail.html"

cp "$TEMPLATES_DIR/discount_form.html" \
   "$TEMPLATES_DIR/tax_form.html"

files=(
    "$VIEWS_DIR/taxes.py"
    "$TEMPLATES_DIR/tax_list.html"
    "$TEMPLATES_DIR/tax_detail.html"
    "$TEMPLATES_DIR/tax_form.html"
)

for file in "${files[@]}"; do
    sed -i \
        -e 's/Discounts/Taxes/g' \
        -e 's/Discount/Tax/g' \
        -e 's/discounts/taxes/g' \
        -e 's/discount/tax/g' \
        "$file"
done

echo
echo "Created:"
printf '  %s\n' "${target_files[@]}"

echo
echo "Review replacements with:"
echo "grep -RniE 'discount|Discount' \\"
echo "  '$VIEWS_DIR/taxes.py' \\"
echo "  '$TEMPLATES_DIR/tax_'*.html"

echo
echo "Next steps:"
echo "1. Add TaxForm to inventory/forms.py"
echo "2. Import tax views in inventory/views/__init__.py"
echo "3. Add tax URLs to inventory/urls.py"
echo "4. Add Taxes to sidebar.html"
echo "5. Run: python manage.py check"
