export async function fetchAs(url, type='json') {
    const response = await fetch(url)

    switch (type) {
        case 'json': return await response.json()
    }
}
