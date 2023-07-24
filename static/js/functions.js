function createCollapsible(element) {
    let content = element.nextElementSibling;
    element.addEventListener("click", function() {
        this.classList.toggle("active");
        if (content.style.display === "block") {
        content.style.display = "none";
        } else {
        content.style.display = "block";
        }
    });
}
document

function buy(product) {
    $.ajax({
        type: "POST",
        url: "/products/" + product.product_id,
        contentType: "application/json",
        success: function(response) {
            // Handle the response from the server
            let qty = document.getElementById("quantity-" + product.product_id)
            let remainingQty = parseInt(response["product"]["quantity"])
            if(remainingQty <= 0) {
                let qtyRow = document.getElementById("quantity-row-" + product.product_id)
                $(qtyRow).remove()
            }

            $(qty).html(remainingQty)
        },
        error: function(error) {
            // Handle any errors that occurred during the AJAX request
            console.error(error);
            alert("An error occurred while submitting the data.");
        }
    });
}