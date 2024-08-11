import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm';

const supabaseUrl = '';
const supabaseKey = '';
const supabase = createClient(supabaseUrl, supabaseKey);

const dataList = document.getElementById('data-list');
const eventFilters = document.getElementById('event-filters');
const messageFilters = document.getElementById('message-filters');

// Event type descriptions
const eventTypes = {
  'Message Created': 'Logs when a message is sent.',
  'Message Edited': 'Logs when a message is edited, including the content before and after the edit.',
  'Message Deleted': 'Logs when a message is deleted, including the content of the deleted message.',
  'Member Join': 'Logs when a new member joins the server.',
  'Member Leave': 'Logs when a member leaves the server.',
  'Channel Created': 'Logs when a new channel is created.',
  'Voice Channel Join': 'Logs when a member joins a voice channel.',
  'Voice Channel Leave': 'Logs when a member leaves a voice channel.',
  'Voice Channel Switch': 'Logs when a member switches from one voice channel to another.',
  'Command Used': 'Logs when a command is used, including the command name, user, and channel.',
  'Role Created': 'Logs when a new role is created.',
  'Role Deleted': 'Logs when a role is deleted.',
  'Role Assigned': 'Logs when a role is assigned to a member.',
  'Server Boost': 'Logs when a member boosts the server.',
  'Emojis Added': 'Logs when new emojis are added to the server.',
  'Emojis Removed': 'Logs when emojis are removed from the server.',
  'Server Updated': 'Logs when the server is updated, including changes in server properties.',
  'User Typing': 'Logs when a user starts typing in a channel.'
};

// Fetch data with optional filter
async function fetchData(filterType = 'event_logs', filterValue = null) {
  try {
    let query;
    if (filterType === 'message_logs') {
      query = supabase.from('message_logs').select('*');
    } else {
      query = supabase.from('event_logs').select('*');
    }
    
    if (filterValue) {
      query = query.eq('event_type', filterValue);
    }
    
    let { data, error } = await query;
    
    if (error) {
      throw error;
    }
    
    displayData(data, filterType);
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

// Display data in the list
function displayData(data, filterType) {
    dataList.innerHTML = '';
    
    data.forEach(item => {
      const listItem = document.createElement('li');
  
      if (filterType === 'message_logs') {
        listItem.innerHTML = `
          <div><img src="${item.avatar_url}"></div>
          <div><strong>ID:</strong> ${item.id}</div>
          <div><strong>User:</strong> ${item.user}</div>
          <div><strong>Content:</strong> ${item.content}</div>
          <div><strong>Channel:</strong> ${item.channel}</div>
          <div><strong>Timestamp:</strong> ${new Date(item.timestamp).toLocaleString()}</div>
        `;
      } else {
        listItem.innerHTML = `
          <div><strong>ID:</strong> ${item.id}</div>
          <div><strong>Event Type:</strong> ${item.event_type}</div>
          <div><strong>Timestamp:</strong> ${new Date(item.timestamp).toLocaleString()}</div>
          <div><strong>Details:</strong> ${item.details || 'No details available.'}</div>
        `;
      }
  
      dataList.appendChild(listItem);
    });
  }
  

// Event listener for filter options
document.querySelectorAll('.filter-options button').forEach(button => {
  button.addEventListener('click', (e) => {
    const filterType = e.target.getAttribute('data-filter-type');
    const filterValue = e.target.getAttribute('data-filter-value');
    fetchData(filterType, filterValue);
  });
});

// Toggle visibility of filter options
document.querySelectorAll('.toggle-button').forEach(button => {
  button.addEventListener('click', () => {
    const filterOptions = button.nextElementSibling;
    filterOptions.style.display = filterOptions.style.display === 'none' || filterOptions.style.display === '' ? 'block' : 'none';
  });
});

// Initial fetch for event_logs
fetchData('event_logs');

// Auto-refresh data every 5 minutes (300000 milliseconds)
setInterval(() => {
  fetchData('event_logs');  // Adjust as needed to refresh both event_logs and message_logs
}, 60000); // 300000 ms = 5 minutes
