function changeContact(itemId, newStatus) {
    if (window.confirm("ステータスを変更します。よろしいですか？")) {
        fetch(`/admin/change_contact/${itemId}/${newStatus}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // window.alert('更新しました')
                window.location.reload(true);
            } else {
                alert('状態の変更に失敗しました。');
            }
        });
    }
}



