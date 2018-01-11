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
                <div class="col-sm-12 col-md-6 col-lg-5 col-xl-4 screenshot">
                    <img src="<%= project.screenshot.url %>" class="img-fluid" />
                    <button class="btn btn-danger btn-block mt-3">Delete screenshot</button>
                </div>
                <div class="col-sm-12 col-md-6 col-lg-7 col-xl-8">
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
                    <button class="btn btn-secondary btn-block">Add string</button>
                </div>
            </div>
        `),

        initialize(projectId, screenshotId) {
            this.initializeProject({
                query: `
                    query ($projectId: ID!, $screenshotId: ID!) {
                        project(id: $projectId) {
                            id
                            name
                            screenshot(id: $screenshotId) {
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
        }
    });
})();
