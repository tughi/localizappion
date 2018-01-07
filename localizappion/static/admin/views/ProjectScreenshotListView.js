Localizappion.ProjectScreenshotListView = Localizappion.ProjectBaseView.extend({
  id: 'project-screenshot-list',

  query: `{
    project(uuid: "PROJECT_UUID") {
      uuid
      name
      screenshots {
        id
      }
    }
  }`,

  template: _.template(`
  `)
})
