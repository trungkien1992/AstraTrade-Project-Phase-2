import 'package:flutter/material.dart';
import '../services/mobile_notification_service.dart';
import '../services/mobile_haptic_service.dart';

/// Mobile settings widget for notifications and haptic preferences
/// Provides user control over mobile-specific features
class MobileSettingsWidget extends StatefulWidget {
  const MobileSettingsWidget({super.key});

  @override
  State<MobileSettingsWidget> createState() => _MobileSettingsWidgetState();
}

class _MobileSettingsWidgetState extends State<MobileSettingsWidget> {
  final _notificationService = MobileNotificationService();
  final _hapticService = MobileHapticService();
  
  bool _notificationsEnabled = true;
  bool _hapticsEnabled = true;
  double _hapticIntensity = 1.0;
  bool _dailyRemindersEnabled = false;
  TimeOfDay _reminderTime = const TimeOfDay(hour: 9, minute: 0);
  
  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    await _notificationService.initialize();
    await _hapticService.initialize();
    
    final notificationSettings = _notificationService.getSettings();
    final hapticSettings = _hapticService.getSettings();
    
    setState(() {
      _notificationsEnabled = notificationSettings['enabled'] ?? true;
      _hapticsEnabled = hapticSettings['enabled'] ?? true;
      _hapticIntensity = hapticSettings['intensity'] ?? 1.0;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Mobile Settings',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            _buildNotificationSection(),
            const Divider(height: 32),
            _buildHapticSection(),
            const Divider(height: 32),
            _buildTestSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.notifications, color: Colors.blue[600]),
            const SizedBox(width: 8),
            Text(
              'Notifications',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        
        // Enable/Disable Notifications
        SwitchListTile(
          title: const Text('Enable Notifications'),
          subtitle: const Text('Trade alerts and achievement notifications'),
          value: _notificationsEnabled,
          onChanged: (value) async {
            await _notificationService.setNotificationsEnabled(value);
            setState(() {
              _notificationsEnabled = value;
            });
          },
        ),
        
        // Daily Reminders
        SwitchListTile(
          title: const Text('Daily Reminders'),
          subtitle: Text('Remind me to trade at ${_reminderTime.format(context)}'),
          value: _dailyRemindersEnabled,
          onChanged: _notificationsEnabled ? (value) async {
            if (value) {
              await _notificationService.scheduleDailyReminder(
                hour: _reminderTime.hour,
                minute: _reminderTime.minute,
              );
            } else {
              await _notificationService.cancelAllNotifications();
            }
            setState(() {
              _dailyRemindersEnabled = value;
            });
          } : null,
        ),
        
        // Reminder Time Picker
        if (_dailyRemindersEnabled)
          ListTile(
            title: const Text('Reminder Time'),
            subtitle: Text(_reminderTime.format(context)),
            trailing: const Icon(Icons.access_time),
            onTap: () async {
              final time = await showTimePicker(
                context: context,
                initialTime: _reminderTime,
              );
              if (time != null) {
                setState(() {
                  _reminderTime = time;
                });
                await _notificationService.scheduleDailyReminder(
                  hour: time.hour,
                  minute: time.minute,
                );
              }
            },
          ),
      ],
    );
  }

  Widget _buildHapticSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.vibration, color: Colors.purple[600]),
            const SizedBox(width: 8),
            Text(
              'Haptic Feedback',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        
        // Enable/Disable Haptics
        SwitchListTile(
          title: const Text('Enable Haptic Feedback'),
          subtitle: const Text('Vibration for trades, achievements, and interactions'),
          value: _hapticsEnabled,
          onChanged: (value) async {
            await _hapticService.setEnabled(value);
            setState(() {
              _hapticsEnabled = value;
            });
            
            if (value) {
              await _hapticService.mediumTap();
            }
          },
        ),
        
        // Haptic Intensity
        if (_hapticsEnabled) ...[
          ListTile(
            title: const Text('Haptic Intensity'),
            subtitle: Text('${(_hapticIntensity * 100).round()}%'),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Slider(
              value: _hapticIntensity,
              min: 0.1,
              max: 2.0,
              divisions: 19,
              label: '${(_hapticIntensity * 100).round()}%',
              onChanged: (value) {
                setState(() {
                  _hapticIntensity = value;
                });
              },
              onChangeEnd: (value) async {
                await _hapticService.setIntensity(value);
                await _hapticService.mediumTap(); // Test the new intensity
              },
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildTestSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.science, color: Colors.green[600]),
            const SizedBox(width: 8),
            Text(
              'Test Features',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        
        // Test Notifications
        if (_notificationsEnabled)
          ListTile(
            title: const Text('Test Notification'),
            subtitle: const Text('Send a test notification'),
            leading: Icon(Icons.notifications_active, color: Colors.blue[600]),
            trailing: const Icon(Icons.send),
            onTap: () async {
              await _notificationService.showTradingAlert(
                title: '📱 Test Notification',
                message: 'This is a test notification from AstraTrade!',
                color: Colors.blue,
              );
              
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Test notification sent!'),
                    duration: Duration(seconds: 2),
                  ),
                );
              }
            },
          ),
        
        // Test Haptics
        if (_hapticsEnabled) ...[
          const Text('Test Haptic Patterns:'),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              _buildHapticTestButton('Light', 'light'),
              _buildHapticTestButton('Medium', 'medium'),
              _buildHapticTestButton('Heavy', 'heavy'),
              _buildHapticTestButton('Success', 'success'),
              _buildHapticTestButton('Achievement', 'achievement'),
              _buildHapticTestButton('Level Up', 'levelup'),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildHapticTestButton(String label, String pattern) {
    return ElevatedButton(
      onPressed: () async {
        await _hapticService.testPattern(pattern);
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.grey[200],
        foregroundColor: Colors.black87,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        minimumSize: const Size(0, 36),
      ),
      child: Text(
        label,
        style: const TextStyle(fontSize: 12),
      ),
    );
  }
}