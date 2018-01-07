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
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="#projects">Projects</a></li>
        <li class="breadcrumb-item"><a href="#projects/<%= project.get('uuid') %>"><%= project.get('name') %></a></li>
        <li class="breadcrumb-item active" aria-current="page">Screenshots</li>
      </ol>
    </nav>
  `)
})
