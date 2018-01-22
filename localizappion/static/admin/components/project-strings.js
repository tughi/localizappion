define(['knockout', 'graphql', 'text!./project-strings.html'], function (ko, graphql, template) {
    'use strict';

    String.prototype.contains = function (chars) {
        return this.indexOf(chars) >= 0;
    };

    function ViewModel(params) {
        this.project = ko.observable();
        this.filter = ko.observable();

        this.filteredStrings = ko.computed(() => {
            let project = this.project();
            if (project) {
                let filter = this.filter();
                if (filter && filter.length > 0) {
                    return ko.utils.arrayFilter(project.strings, string => {
                        return string.name.contains(filter) || string.valueOther.contains(filter) || (string.valueOne && string.valueOne.contains(filter));
                    });
                }
                return project.strings;
            }
        });

        graphql({
            query: `
                query ($projectId: ID!) {
                    project(id: $projectId) {
                        strings {
                            name
                            valueOne
                            valueOther
                        }
                    }
                }
            `,
            variables: {
                projectId: params.projectId
            }
        }).then(response => {
            this.project(response.data.project);
        });
    }

    return {
        template,
        viewModel: ViewModel
    };
});

