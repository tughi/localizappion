$(function () {
    $('html').on('dragover drop', event => {
        event.preventDefault()
    })

    var router = new Localizappion.Router()

    if (!Backbone.history.start()) {
        router.navigate('projects', { trigger: true })
    }
})
