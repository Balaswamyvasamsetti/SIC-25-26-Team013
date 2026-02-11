import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
  Chip,
  Avatar,
  Badge,
  useMediaQuery,
  useTheme,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Switch,
  FormControlLabel,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications,
  Settings,
  LightMode,
  DarkMode,
  Person,
  Logout,
  Info,
  Warning,
  CheckCircle,
  Speed,
  VolumeUp,
  FileDownload,
  Keyboard,
} from '@mui/icons-material';
import { useThemeMode } from '../contexts/ThemeContext';
import { useAppContext } from '../contexts/AppContext';
import ExportDialog from './ExportDialog';

const TopBar = ({ onMenuClick }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { mode, toggleMode } = useThemeMode();
  const { conversations, resumeData } = useAppContext();
  
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [settings, setSettings] = useState({
    notifications: true,
    autoSave: true,
    soundEffects: false,
  });

  const notifications = [
    {
      id: 1,
      type: 'success',
      title: 'Document Processed',
      message: 'research_paper.pdf has been successfully indexed',
      time: '2 minutes ago',
    },
    {
      id: 2,
      type: 'info',
      title: 'System Update',
      message: 'New quantum retrieval algorithms deployed',
      time: '1 hour ago',
    },
    {
      id: 3,
      type: 'warning',
      title: 'Storage Warning',
      message: 'Document storage is 85% full',
      time: '3 hours ago',
    },
  ];

  const handleSettingChange = (setting) => {
    setSettings(prev => ({ ...prev, [setting]: !prev[setting] }));
  };

  const handleUserMenuClick = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle color="success" />;
      case 'warning': return <Warning color="warning" />;
      case 'info': return <Info color="info" />;
      default: return <Info />;
    }
  };



  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        backgroundColor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
        color: 'text.primary',
      }}
    >
      <Toolbar sx={{ minHeight: '64px !important', px: { xs: 2, sm: 3 } }}>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 3 }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 600, cursor: 'pointer' }}>
            AI Research Agent
          </Typography>
        </Box>

        {/* Right side actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Export data">
            <IconButton 
              color="inherit" 
              size="small"
              onClick={() => setExportOpen(true)}
            >
              <FileDownload />
            </IconButton>
          </Tooltip>

          <Tooltip title="Keyboard shortcuts">
            <IconButton 
              color="inherit" 
              size="small"
              onClick={() => setShortcutsOpen(true)}
            >
              <Keyboard />
            </IconButton>
          </Tooltip>

          <Tooltip title={`Switch to ${mode === 'dark' ? 'light' : 'dark'} mode`}>
            <IconButton 
              color="inherit" 
              size="small"
              onClick={toggleMode}
            >
              {mode === 'dark' ? <LightMode /> : <DarkMode />}
            </IconButton>
          </Tooltip>

          <Badge badgeContent={notifications.length} color="primary">
            <IconButton 
              color="inherit" 
              size="small"
              onClick={() => setNotificationsOpen(true)}
            >
              <Notifications />
            </IconButton>
          </Badge>

          <IconButton 
            color="inherit" 
            size="small"
            onClick={() => setSettingsOpen(true)}
          >
            <Settings />
          </IconButton>

          <Avatar
            sx={{
              width: 32,
              height: 32,
              backgroundColor: 'primary.main',
              fontSize: '0.875rem',
              fontWeight: 600,
              ml: 1,
              cursor: 'pointer',
            }}
            onClick={handleUserMenuClick}
          >
            U
          </Avatar>
        </Box>
      </Toolbar>

      {/* User Menu */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleUserMenuClose}>
          <ListItemIcon><Person /></ListItemIcon>
          <ListItemText>Profile</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => { handleUserMenuClose(); setSettingsOpen(true); }}>
          <ListItemIcon><Settings /></ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleUserMenuClose}>
          <ListItemIcon><Logout /></ListItemIcon>
          <ListItemText>Logout</ListItemText>
        </MenuItem>
      </Menu>

      {/* Notifications Dialog */}
      <Dialog
        open={notificationsOpen}
        onClose={() => setNotificationsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Notifications</DialogTitle>
        <DialogContent>
          <List>
            {notifications.map((notification) => (
              <ListItem key={notification.id}>
                <ListItemIcon>
                  {getNotificationIcon(notification.type)}
                </ListItemIcon>
                <ListItemText
                  primary={notification.title}
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {notification.message}
                      </Typography>
                      <Typography variant="caption" color="text.disabled">
                        {notification.time}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNotificationsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Settings</DialogTitle>
        <DialogContent>
          <List>
            <ListItem>
              <ListItemIcon><Notifications /></ListItemIcon>
              <ListItemText primary="Enable Notifications" />
              <Switch
                checked={settings.notifications}
                onChange={() => handleSettingChange('notifications')}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><Speed /></ListItemIcon>
              <ListItemText primary="Auto-save Conversations" />
              <Switch
                checked={settings.autoSave}
                onChange={() => handleSettingChange('autoSave')}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><VolumeUp /></ListItemIcon>
              <ListItemText primary="Sound Effects" />
              <Switch
                checked={settings.soundEffects}
                onChange={() => handleSettingChange('soundEffects')}
              />
            </ListItem>
            <Divider sx={{ my: 2 }} />
            <ListItem>
              <FormControlLabel
                control={
                  <Switch
                    checked={mode === 'dark'}
                    onChange={toggleMode}
                  />
                }
                label="Dark Mode"
              />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Export Dialog */}
      <ExportDialog
        open={exportOpen}
        onClose={() => setExportOpen(false)}
        conversations={conversations}
        resumeAnalysis={resumeData?.analysis}
      />

      {/* Keyboard Shortcuts Dialog */}
      <Dialog
        open={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Keyboard Shortcuts</DialogTitle>
        <DialogContent>
          <List dense>
            <ListItem>
              <ListItemText
                primary="Ctrl + D"
                secondary="Toggle dark mode"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Ctrl + B"
                secondary="Toggle sidebar"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Ctrl + Enter"
                secondary="Send query (in chat)"
              />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShortcutsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </AppBar>
  );
};

export default TopBar;