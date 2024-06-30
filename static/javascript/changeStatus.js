function changeStatus(itemId, newStatus){
    if (window.confirm("ステータスを変更します。よろしいですか？")) {
        fetch(`/admin/change_status/${itemId}/${newStatus}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('状態の変更に失敗しました。');
            }
        });
    }
}