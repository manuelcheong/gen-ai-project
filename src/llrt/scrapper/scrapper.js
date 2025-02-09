// eslint-disable-next-line import/prefer-default-export
/**
 * Handles the event for the pipe reader.
 * @param {Object} event - The event object.
 * @returns {boolean} - Returns true.
 */
export const handler = async (event) => {
  console.log('------ PIPE READER LLRT 😎 CANARY DEPLOYMENT 🐙 AND LLRT WITH SDK 🐀 -----------');
  console.log(JSON.stringify(event));

  return true;
};



//   LLRT lambda arm64 no sdk


