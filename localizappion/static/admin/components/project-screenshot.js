define(['knockout', 'text!./project-screenshot.html', 'graphql'], function (ko, template, graphql) {
    'use strict';

    function ViewModel(params) {
        this.allProjects = ko.observable();
        this.project = ko.observable();
        this.screenshotId = ko.observable(params.screenshotId);
        this.screenshotName = ko.observable(params.name);
        this.screenshotUrl = ko.observable();
        this.screenshotStrings = ko.observableArray([]);
        this.activeScreenshotString = ko.observable();
        this.hoveredScreenshotString = ko.observable();
        this.showAddStringDialog = ko.observable(false);
        this.availableStringsFilter = ko.observable();

        this.availableStrings = ko.computed(function () {
            let availableStringsFilter = this.availableStringsFilter();
            if (availableStringsFilter) {
                return ko.utils.arrayFilter(this.project().strings, string => {
                    // TODO: exclude already added strings
                    return string.valueOther.indexOf(availableStringsFilter) >= 0 || (string.valueOne && string.valueOne.indexOf(availableStringsFilter) >= 0);
                });
            }
            return [];
        }, this);

        this.clearHoveredScreenshotString = (event) => {
            this.hoveredScreenshotString(null);
        };

        this.addString = (string) => {
            const screenshotString = {
                area: ko.observable('(0,0)x(5,5)'),
                string
            };
            this.screenshotStrings.push(screenshotString);
            this.activeScreenshotString(screenshotString);

            this.showAddStringDialog(false);
        };

        this.save = () => {
            graphql({
                query: `
                    mutation ($projectId: ID!, $screenshotId: ID, $screenshotName: String!, $screenshotData: String, $screenshotStrings: [ScreenshotStringInputType]!) {
                        saveProjectScreenshot(projectId: $projectId, screenshotId: $screenshotId, screenshotName: $screenshotName, screenshotData: $screenshotData, screenshotStrings: $screenshotStrings) {
                            screenshot {
                                id
                                url
                                name
                                screenshotStrings {
                                    id
                                    area
                                    string {
                                        id
                                    }
                                }
                            }
                        }
                    }
                `,
                variables: {
                    projectId: params.projectId,
                    screenshotId: this.screenshotId() || undefined,
                    screenshotName: this.screenshotName(),
                    screenshotData: this.screenshotUrl().indexOf('data:') == 0 && this.screenshotUrl() || undefined,
                    screenshotStrings: ko.utils.arrayMap(this.screenshotStrings(), screenshotString => {
                        return {
                            id: screenshotString.id || null,
                            area: screenshotString.area(),
                            stringId: screenshotString.string.id,
                        };
                    })
                }
            }).then(response => {
                let projectStrings = this.project().strings;
                let screenshot = response.data.saveProjectScreenshot.screenshot;
                this.screenshotId(screenshot.id);
                this.screenshotName(screenshot.name);
                this.screenshotUrl(screenshot.url);
                this.screenshotStrings(screenshot.screenshotStrings.map(screenshotString => {
                    return {
                        id: screenshotString.id,
                        area: ko.observable(screenshotString.area),
                        string: projectStrings.find(projectString => projectString.id === screenshotString.string.id)
                    };
                }));
                this.activeScreenshotString(null);
            });
        };

        graphql({
            query: `
                query ($projectId: ID!, $screenshotId: ID) {
                    project(id: $projectId) {
                        id
                        screenshot(id: $screenshotId) {
                            id
                            url
                            name
                            screenshotStrings {
                                id
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
                    allProjects: projects {
                        id
                        name
                    }
                }
            `,
            variables: {
                projectId: params.projectId,
                screenshotId: this.screenshotId() || null
            }
        }).then(response => {
            this.allProjects(response.data.allProjects);
            const project = response.data.project;
            this.project(project);
            const screenshot = project.screenshot;
            if (screenshot) {
                this.screenshotId(screenshot.id);
                this.screenshotName(screenshot.name);
                this.screenshotUrl(screenshot.url);
                this.screenshotStrings(screenshot.screenshotStrings.map(screenshotString => {
                    return {
                        id: screenshotString.id,
                        area: ko.observable(screenshotString.area),
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
