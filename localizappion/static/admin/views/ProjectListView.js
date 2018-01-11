Localizappion.ProjectListView = Backbone.View.extend({
    id: 'project-list',

    template: _.template(`
        <div class="list-group">
            <% _.each(projects, project => { %>
                <a class="list-group-item list-group-item-action" href="#projects/<%= project.id %>"><%= project.name %></a>
            <% }) %>
        </div>
    `),

    initialize() {
        this.model = new Backbone.Model();

        graphql({
            query: `
                query {
                    projects {
                        id
                        name
                    }
                }
            `
        }).then(response => {
            this.model.set({ projects: response.data.projects });
        });

        this.listenTo(this.model, 'change:projects', this.render);
    },

    render() {
        this.$el.empty();

        if (this.model.has('projects')) {
            this.$el.html(this.template(this.model.attributes));
        }

        return this;
    }
})
