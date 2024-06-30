function deleteItem(itemId){
    if (window.confirm("商品を削除します。よろしいですか？")) {
        fetch(`/admin/delete_item/${itemId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // window.alert('削除しました')
                window.location.reload(true);
            } else {
                alert('削除に失敗しました。');
            }
        });
    }
}