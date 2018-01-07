$(function () {
  var router = new Localizappion.Router()

  if (!Backbone.history.start()) {
    router.navigate('projects', { trigger: true })
  }
})