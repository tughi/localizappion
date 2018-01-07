Localizappion.ProjectDetailView = Localizappion.ProjectBaseView.extend({
    id: 'project-detail',

    query: `{
        project(uuid: "PROJECT_UUID") {
            uuid
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
    }`,

    template: _.template(`
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="#projects">Projects</a></li>
                <li class="breadcrumb-item active" aria-current="page"><%= project.get('name') %></a></li>
            </ol>
        </nav>

        <p>
            <div class="list-group">
                <a class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" href="#projects/<%= project.get('uuid') %>/strings">
                    Strings
                    <span class="badge badge-primary badge-pill"><%= project.get('stringsCount') %></span>
                </a>
                <a class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" href="#projects/<%= project.get('uuid') %>/screenshots">
                    Screenshots
                    <span class="badge badge-primary badge-pill"><%= project.get('screenshotsCount') %></span>
                </a>
            </div>
        </p>

        <p>
            <div class="list-group">
                <% _.each(project.get('translations'), function(translation) { %>
                    <a class="list-group-item list-group-item-action" href="#projects/<%= project.get('uuid') %>/translations/"><%= translation.language.name %></a>
                <% }) %>
            </div>
        </p>
    `)
})
