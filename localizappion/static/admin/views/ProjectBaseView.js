Localizappion.ProjectBaseView = Backbone.View.extend({
    initializeProject(options) {
        this.model = new Backbone.Model();

        graphql(options)
            .then(response => {
                this.model.set({
                    project: response.data.project
                });
            });

        this.listenTo(this.model, 'change:project', this.render);
    },

    render() {
        this.$el.empty();

        if (this.model.has('project')) {
            this.$el.html(this.template(this.model.attributes));
        }

        return this;
    }
})
