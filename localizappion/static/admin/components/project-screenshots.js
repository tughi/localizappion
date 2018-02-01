define(['knockout', 'text!./project-screenshots.html', 'graphql', 'hasher'], function (ko, template, graphql, hasher) {
    'use strict';

    function ViewModel(params) {
        this.allProjects = ko.observable();
        this.project = ko.observable();
        this.screenshots = ko.observableArray();
        this.screenshotName = ko.observable();

        this.filteredScreenshots = ko.computed(function () {
            if (this.screenshotName()) {
                return ko.utils.arrayFilter(this.screenshots(), screenshot => screenshot.name.indexOf(this.screenshotName()) >= 0);
            }

            return this.screenshots();
        }, this);

        this.createScreenshot = function (self) {
            hasher.setHash(`projects/${self.project().id}/screenshots/new/${self.screenshotName() || 'unnamed'}`);
        };

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
                    allProjects: projects {
                        id
                        name
                    }
                }
            `,
            variables: {
                projectId: params.projectId
            }
        }).then(response => {
            this.allProjects(response.data.allProjects);
            this.project(response.data.project);
            this.screenshots(response.data.project.screenshots);
        });
    };

    return {
        template: template,
        viewModel: ViewModel
    };
});
