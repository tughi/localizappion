Localizappion.ProjectListView = Backbone.View.extend({
    id: 'project-list',

    template: _.template(`
        <div class="list-group">
            <% projects.each(project => { %>
                <a class="list-group-item list-group-item-action" href="#projects/<%= project.get('uuid') %>"><%= project.get('name') %></a>
            <% }) %>
        </div>
    `),

    initialize() {
        var projects = this.projects = new Backbone.Collection()

        $.post(
            'graphql',
            {
                query: `{
                    projects {
                        uuid
                        name
                    }
                }`
            }
        ).then(response => {
            projects.reset(response.data.projects)
        })

        this.listenTo(projects, 'reset', this.render)
    },

    render() {
        this.$el.empty()

        if (this.projects) {
            this.$el.html(this.template({ projects: this.projects }))
        }

        return this
    }
})
