function filterProducts() {
  // Lấy giá trị của droplist
  var filterBy = document.getElementById("filter").value;

  // Gọi API để lấy dữ liệu sản phẩm được lọc
  fetch(`/all-product?filter=${filterBy}`)
    .then((response) => response.json())
    .then((data) => {
      // Render lại danh sách sản phẩm sau khi lọc
      renderProducts(data);
    })
    .catch((error) => console.error("Error:", error));
}

function renderProducts(allProducts) {
  const row = document.querySelector(".row");
  row.innerHTML = ""; // Xóa bỏ tất cả sản phẩm hiện tại trên trang

  allProducts.forEach((product) => {
    const col = document.createElement("div");
    col.classList.add("col-4");

    const link = document.createElement("a");
    link.href = `/product_detail/${product[0]}`;

    const image = document.createElement("img");
    image.style.aspectRatio = "3/4";
    image.style.objectFit = "cover";
    image.src = product[5];
    link.appendChild(image);

    const detailDiv = document.createElement("div");
    detailDiv.classList.add("detail");

    const heading = document.createElement("h4");
    heading.textContent = product[1];
    detailDiv.appendChild(heading);

    const ratingDiv = document.createElement("div");
    ratingDiv.classList.add("rating");

    const rate = parseInt(product[3]);
    for (let i = 0; i < 5; i++) {
      const star = document.createElement("i");
      star.classList.add("fa");
      if (i < rate) {
        star.classList.add("fa-star");
      } else {
        star.classList.add("fa-star-o");
      }
      ratingDiv.appendChild(star);
    }

    const ratingSpan = document.createElement("span");
    ratingSpan.style.marginLeft = "2rem";
    ratingSpan.textContent = product[2];
    ratingDiv.appendChild(ratingSpan);

    const description = document.createElement("p");
    description.textContent = product[6];

    detailDiv.appendChild(ratingDiv);
    detailDiv.appendChild(description);

    col.appendChild(link);
    col.appendChild(detailDiv);

    row.appendChild(col);
  });
}
