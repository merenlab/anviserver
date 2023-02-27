export const ValidateProps = {
  user: {
    username: { type: 'string', minLength: 4, maxLength: 20 },
    name: { type: 'string', minLength: 1, maxLength: 50 },
    password: { type: 'string', minLength: 8 },
    email: { type: 'string', minLength: 1 },
    bio: { type: 'string', minLength: 0, maxLength: 160 },
  },
  post: {
    content: { type: 'string', minLength: 1, maxLength: 280 },
  },
  comment: {
    content: { type: 'string', minLength: 1, maxLength: 280 },
  },
  submission: {
    title: { type: 'string', minLength: 1, maxLength: 280 },
    desc: { type: 'string', minLength: 1, maxLength: 280 },
    name: { type: 'string', minLength: 1, maxLength: 280 },
    email: { type: 'string', minLength: 1, maxLength: 280 },
    affiliation: { type: 'string', minLength: 1, maxLength: 280 },
    web: { type: 'string', minLength: 1, maxLength: 280 },
    workdir: { type: 'string', minLength: 1, maxLength: 280 },
    setup: { type: 'string', minLength: 1, maxLength: 500 },
    run: { type: 'string', minLength: 1, maxLength: 500 },
  },
};
