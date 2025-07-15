module.exports = {
  handler: async (event) => {
    console.log('------ INSERT VECTORS FAISS  🐀 -----------');
    console.log(JSON.stringify(event));
    return true;
  },
};
