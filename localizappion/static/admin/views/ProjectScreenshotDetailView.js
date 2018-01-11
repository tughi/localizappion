Localizappion.ProjectScreenshotDetailView = (function () {
    return Localizappion.ProjectBaseView.extend({
        id: 'project-screenshot-detail',

        template: _.template(`
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="#projects">Projects</a></li>
                    <li class="breadcrumb-item"><a href="#projects/<%= project.id %>"><%= project.name %></a></li>
                    <li class="breadcrumb-item"><a href="#projects/<%= project.id %>/screenshots">Screenshots</a></li>
                    <li class="breadcrumb-item active" aria-current="page"><%= project.screenshot.name %></li>
                </ol>
            </nav>

            <div class="row mb-3">
                <div id="screenshot" class="col-sm-12 col-md-5 col-xl-4">
                    <img src="<%= project.screenshot.url %>" class="mb-3"/>
                    <button id="delete-screenshot" class="btn btn-danger btn-block mb-3">Delete screenshot</button>
                </div>
                <div class="col-sm-12 col-md-7 col-xl-8">
                    <% if (project.screenshot.strings.length) { %>
                        <div class="list-group mb-3">
                            <% _.each(project.screenshot.strings, string => { %>
                                <div class="list-group-item list-group-item-action">
                                    <h5 class="mb-1"><%= string.string.valueOther %></h5>
                                    <small class="text-muted"><%= string.string.name %></small>
                                </div>
                            <% }) %>
                        </div>
                    <% } %>
                    <button id="add-string" class="btn btn-secondary btn-block">Add string</button>
                </div>
            </div>
        `),

        events: {
            'click #add-string': 'onAddString',
            'click #delete-screenshot': 'onDeleteScreenshot',
        },

        initialize(projectId, screenshotId) {
            this.initializeProject({
                query: `
                    query ($projectId: ID!, $screenshotId: ID!) {
                        project(id: $projectId) {
                            id
                            name
                            screenshot(id: $screenshotId) {
                                id
                                name
                                url
                                strings {
                                    area
                                    string {
                                        name
                                        valueOne
                                        valueOther
                                    }
                                }
                            }
                        }
                    }
                `,
                variables: { projectId, screenshotId }
            });

            this.model.set({
                stringQuery: null
            });
        },

        onAddString() {
            // TODO: add string
        },

        onDeleteScreenshot() {
            var project = this.model.get('project');
            // TODO: use bootstrap modal
            if (prompt('Delete screenshot? (yes/no)') === 'yes') {
                graphql({
                    query: `
                        mutation($projectId: ID!, $screenshotId: ID!) {
                            deleteProjectScreenshot(projectId: $projectId, screenshotId: $screenshotId) {
                                ok
                            }
                        }
                    `,
                    variables: {
                        projectId: project.id,
                        screenshotId: project.screenshot.id
                    }
                }).then(response => {
                    if (response.data.deleteProjectScreenshot.ok) {
                        Localizappion.router.navigate(`projects/${project.id}/screenshots`, { trigger: true })
                    }
                });
            }
        }
    });
})();
