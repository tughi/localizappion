if (!Localizappion) {
  var Localizappion = {}
}

Localizappion.Router = Backbone.Router.extend({
  routes: {
    'projects': 'showProjectList',
    'projects/:uuid': 'showProjectDetail',
    'projects/:uuid/screenshots': 'showProjectScreenshotList',
  },

  initialize() {
    this.view = null
  },

  execute(callback, args, name) {
    if (this.view) {
      this.view.remove()
    }

    if (callback) {
      this.view = callback.apply(this, args);

      if (this.view) {
        $('#app').append(this.view.render().$el);
      }
    }
  },

  showProjectList() {
    return new Localizappion.ProjectListView()
  },

  showProjectDetail(uuid) {
    return new Localizappion.ProjectDetailView(uuid)
  },

  showProjectScreenshotList(uuid) {
    return new Localizappion.ProjectScreenshotListView(uuid)
  }
})
