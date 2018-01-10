if (!Localizappion) {
    var Localizappion = {}
}

Localizappion.Router = Backbone.Router.extend({
    routes: {
        'projects': 'showProjectList',
        'projects/:projectId': 'showProjectDetail',
        'projects/:projectId/screenshots': 'showProjectScreenshotList',
        'projects/:projectId/screenshots/:screenshotId': 'showProjectScreenshotDetail',
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

    showProjectDetail(projectId) {
        return new Localizappion.ProjectDetailView(projectId)
    },

    showProjectScreenshotList(projectId) {
        return new Localizappion.ProjectScreenshotListView(projectId)
    },

    showProjectScreenshotDetail(projectId, screenshotId) {
        return new Localizappion.ProjectScreenshotDetailView(projectId, screenshotId)
    }
})
