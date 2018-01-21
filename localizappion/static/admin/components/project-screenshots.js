define(['knockout', 'text!./project-screenshots.html', 'graphql'], function (ko, template, graphql) {
    'use strict';

    function ViewModel(params) {
        this.project = ko.observable();
        this.screenshots = ko.observableArray();
        this.screenshotName = ko.observable();

        this.filteredScreenshots = ko.computed(function () {
            if (this.screenshotName()) {
                return ko.utils.arrayFilter(this.screenshots(), screenshot => screenshot.name.indexOf(this.screenshotName()) >= 0);
            }

            return this.screenshots();
        }, this);

        graphql({
            query: `
                query ($projectId: ID!) {
                    project(id: $projectId) {
                        id
                        name
                        screenshots {
                            id
                            url
                            name
                            screenshotStrings {
                                area
                            }
                        }
                    }
                }
            `,
            variables: {
                projectId: params.projectId
            }
        }).then(response => {
            this.project(response.data.project);
            this.screenshots(response.data.project.screenshots);
        });
    };

    return {
        template: template,
        viewModel: ViewModel
    };
});
