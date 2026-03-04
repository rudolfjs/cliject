LIST_VIEWER_PROJECTS = """
query ListViewerProjects($cursor: String) {
  viewer {
    projectsV2(first: 50, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        id
        number
        title
        shortDescription
        closed
        updatedAt
        url
        items {
          totalCount
        }
      }
    }
  }
}
"""

LIST_ORG_PROJECTS = """
query ListOrgProjects($org: String!, $cursor: String) {
  organization(login: $org) {
    projectsV2(first: 50, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        id
        number
        title
        shortDescription
        closed
        updatedAt
        url
        items {
          totalCount
        }
      }
    }
  }
}
"""

GET_PROJECT_FIELDS = """
query GetProjectFields($owner: String!, $number: Int!, $isOrg: Boolean!) {
  viewer @skip(if: $isOrg) {
    projectV2(number: $number) {
      id
      title
      number
      shortDescription
      closed
      updatedAt
      url
      items {
        totalCount
      }
      fields(first: 50) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
              color
              description
            }
          }
          ... on ProjectV2Field {
            id
            name
          }
          ... on ProjectV2IterationField {
            id
            name
          }
        }
      }
    }
  }
  organization(login: $owner) @include(if: $isOrg) {
    projectV2(number: $number) {
      id
      title
      number
      shortDescription
      closed
      updatedAt
      url
      items {
        totalCount
      }
      fields(first: 50) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
              color
              description
            }
          }
          ... on ProjectV2Field {
            id
            name
          }
          ... on ProjectV2IterationField {
            id
            name
          }
        }
      }
    }
  }
}
"""

GET_PROJECT_ITEMS = """
query GetProjectItems($owner: String!, $number: Int!, $isOrg: Boolean!, $cursor: String) {
  viewer @skip(if: $isOrg) {
    projectV2(number: $number) {
      items(first: 100, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2SingleSelectField {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldTextValue {
                text
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldDateValue {
                date
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldNumberValue {
                number
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
              }
            }
          }
          content {
            ... on Issue {
              title
              number
              url
              state
              repository {
                nameWithOwner
              }
              assignees(first: 5) {
                nodes {
                  login
                  avatarUrl
                }
              }
              labels(first: 10) {
                nodes {
                  name
                  color
                }
              }
            }
            ... on PullRequest {
              title
              number
              url
              state
              repository {
                nameWithOwner
              }
              assignees(first: 5) {
                nodes {
                  login
                  avatarUrl
                }
              }
              labels(first: 10) {
                nodes {
                  name
                  color
                }
              }
            }
            ... on DraftIssue {
              title
              assignees(first: 5) {
                nodes {
                  login
                  avatarUrl
                }
              }
            }
          }
        }
      }
    }
  }
  organization(login: $owner) @include(if: $isOrg) {
    projectV2(number: $number) {
      items(first: 100, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2SingleSelectField {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldTextValue {
                text
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldDateValue {
                date
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldNumberValue {
                number
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
              }
            }
          }
          content {
            ... on Issue {
              title
              number
              url
              state
              repository {
                nameWithOwner
              }
              assignees(first: 5) {
                nodes {
                  login
                  avatarUrl
                }
              }
              labels(first: 10) {
                nodes {
                  name
                  color
                }
              }
            }
            ... on PullRequest {
              title
              number
              url
              state
              repository {
                nameWithOwner
              }
              assignees(first: 5) {
                nodes {
                  login
                  avatarUrl
                }
              }
              labels(first: 10) {
                nodes {
                  name
                  color
                }
              }
            }
            ... on DraftIssue {
              title
              assignees(first: 5) {
                nodes {
                  login
                  avatarUrl
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
