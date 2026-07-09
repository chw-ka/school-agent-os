/**
 * Reads runtime config. SCHOOLINK_KEY must be set manually under
 * Project Settings > Script Properties — never hard-code it here or
 * put it in a sheet cell.
 */
function getConfig_() {
  const props = PropertiesService.getScriptProperties();
  const key = props.getProperty('SCHOOLINK_KEY');
  if (!key) {
    throw new Error('SCHOOLINK_KEY not set. Project Settings > Script Properties > add SCHOOLINK_KEY.');
  }
  return {
    baseUrl: props.getProperty('SCHOOLINK_BASE_URL') || 'https://chw.schoolink.hk',
    key: key,
    messageTypeId: props.getProperty('MESSAGE_TYPE_ID') || '640',
  };
}
