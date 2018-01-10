Localizappion.ProjectScreenshotDetailView = Localizappion.ProjectBaseView.extend({
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
                                }
                            }
                        }
                    }
                }
            `,
            variables: { projectId, screenshotId }
        });

        this.model.set({ uploads: [] });
    }
});
