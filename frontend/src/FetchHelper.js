import Cookies from 'js-cookie'

export function doFetch(url, payload) {
    const csrftoken = Cookies.get('csrftoken');  // reference https://docs.djangoproject.com/en/3.2/ref/csrf/ 
    payload['mode'] = 'same-origin';
    payload['headers'] = {'X-CSRFToken': csrftoken};
    return fetch(url, payload);
}

export function doFetchPost(url, bodyDict) {
    let bodyJson = JSON.stringify(bodyDict);
    return doFetch(url, {
        method: 'POST',
        body: bodyJson
    });
}

export function doFetchPut(url, bodyDict) {
    let bodyJson = JSON.stringify(bodyDict);
    return doFetch(url, {
        method: 'PUT',
        body: bodyJson
    });
}

export function doFetchDelete(url, bodyDict) {
    let bodyJson = JSON.stringify(bodyDict);
    return doFetch(url, {
        method: 'DELETE',
        body: bodyJson
    });
}
