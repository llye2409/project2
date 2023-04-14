function sortProductsByPriceAscending(products) {
    return products.sort((a, b) => a.price - b.price);
  }
  
  const sortButton = document.getElementById('sort-select');
  sortButton.addEventListener('click', function() {
    const sortedProducts = sortProductsByPriceAscending(products); // gọi hàm sắp xếp ở đây
    displayProducts(sortedProducts); // hiển thị sản phẩm sau khi đã được sắp xếp
  });

  const sortSelect = document.querySelector('.filter__sort select');
sortSelect.addEventListener('change', function() {
  const sortValue = this.value; // Lấy giá trị của select
  sortProducts(sortValue); // Gọi hàm sắp xếp sản phẩm với giá trị của select
});



