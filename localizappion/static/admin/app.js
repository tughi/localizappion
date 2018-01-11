$(function () {
    $('html').on('dragover drop', event => {
        event.preventDefault()
    })

    Localizappion.router = new Localizappion.Router()

    if (!Backbone.history.start()) {
        Localizappion.router.navigate('projects', { trigger: true })
    }
})
