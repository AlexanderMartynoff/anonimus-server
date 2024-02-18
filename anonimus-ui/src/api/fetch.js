export async function fetchAs(url,  mapper=(v) => v, type='json') {
    const response = await fetch(url)

    switch (type) {
        case 'json': return mapper(await response.json())
    }

    return await response.text()
}
