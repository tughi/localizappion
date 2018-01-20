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

        this.addString = (string) => {
            const screenshotString = {
                area: '(0,0)x(5,5)',
                string
            };
            this.screenshotStrings.push(screenshotString);
            this.activeScreenshotString(screenshotString);

            this.showAddStringDialog(false);
        };

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
