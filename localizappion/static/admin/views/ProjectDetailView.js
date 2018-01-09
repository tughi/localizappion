Localizappion.ProjectDetailView = Localizappion.ProjectBaseView.extend({
    id: 'project-detail',

    template: _.template(`
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="#projects">Projects</a></li>
                <li class="breadcrumb-item active" aria-current="page"><%= project.name %></a></li>
            </ol>
        </nav>

        <p>
            <div class="list-group">
                <a class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" href="#projects/<%= project.id %>/strings">
                    Strings
                    <span class="badge badge-primary badge-pill"><%= project.stringsCount %></span>
                </a>
                <a class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" href="#projects/<%= project.id %>/screenshots">
                    Screenshots
                    <span class="badge badge-primary badge-pill"><%= project.screenshotsCount %></span>
                </a>
            </div>
        </p>

        <p>
            <div class="list-group">
                <% _.each(project.translations, function(translation) { %>
                    <a class="list-group-item list-group-item-action" href="#projects/<%= project.id %>/translations/"><%= translation.language.name %></a>
                <% }) %>
            </div>
        </p>
    `),

    initialize(projectId) {
        this.initializeProject({
            query: `
                query ($id: ID!) {
                    project(id: $id) {
                        id
                        name
                        stringsCount
                        screenshotsCount
                        translations {
                            uuid
                            language {
                                name
                            }
                        }
                    }
                }
            `,
            variables: { id: projectId }
        })
    }
})
