
function tail(str, length) {
    return str.slice(str.length - (length || 5))
}

export {
    tail,
}
