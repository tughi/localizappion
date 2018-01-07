var Localizappion = {}

Localizappion.ProjectBaseView = Backbone.View.extend({
  initialize(uuid) {
    var project = this.project = new Backbone.Model()

    $.post('graphql', { query: this.query.replace('PROJECT_UUID', uuid) })
      .then(response => {
        project.set(response.data.project)
      })

    this.listenTo(project, 'change', this.render)
  },

  render() {
    this.$el.empty()

    if (this.project.get('name')) {
      this.$el.html(this.template({ project: this.project }))
    }

    return this
  }
})
