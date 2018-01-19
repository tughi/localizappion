define(['knockout', 'text!./project-screenshot.html', 'graphql'], function (ko, template, graphql) {
    'use strict';

    function ViewModel(params) {
        this.project = ko.observable();
        this.screenshotId = params.screenshotId;
        this.screenshotName = ko.observable(params.name);
        this.screenshotUrl = ko.observable();
        this.screenshotStrings = ko.observableArray([]);
        this.activeScreenshotString = ko.observable();
        this.hoveredScreenshotString = ko.observable();

        graphql({
            query: params.screenshotId ? `
                query ($projectId: ID!, $screenshotId: ID!) {
                    project(id: $projectId) {
                        id
                        screenshot(id: $screenshotId) {
                            url
                            name
                            strings {
                                area
                                string {
                                    id
                                }
                            }
                        }
                        strings {
                            id
                            name
                            valueOne
                            valueOther
                        }
                    }
                }
            ` : `
                query ($projectId: ID!) {
                    project(id: $projectId) {
                        id
                        strings {
                            id
                            name
                            valueOne
                            valueOther
                        }
                    }
                }
            `,
            variables: ko.utils.extend({ projectId: params.projectId }, params.screenshotId ? { screenshotId: params.screenshotId } : null),
        }).then(response => {
            const project = response.data.project;
            this.project(project);
            const screenshot = project.screenshot;
            if (screenshot) {
                this.screenshotName(screenshot.name);
                this.screenshotUrl(screenshot.url);
                this.screenshotStrings(screenshot.strings.map(screenshotString => {
                    return {
                        area: screenshotString.area,
                        string: project.strings.find(projectString => projectString.id === screenshotString.string.id)
                    };
                }));
            }
        });
    };

    return {
        template: template,
        viewModel: ViewModel
    };
});
