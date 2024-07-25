function deleteContact(contactId) {
    if (window.confirm('本当に削除しますか？')) {
        fetch(`/admin/delete_contact/${contactId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload(true);
            } else {
                alert('削除に失敗しました');
            }
        });
    }
}