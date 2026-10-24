# Mobile App Development Guide 📱

## Quick Start for Mobile Developer

### Backend Setup (5 minutes)

1. **Clone and run the backend**:
   ```bash
   git clone https://github.com/Tanob1/Hackachusetts2026-Clinical_Trial_Matcher.git
   cd Hackachusetts2026-Clinical_Trial_Matcher
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   python database.py
   python data/load_data.py
   python app.py
   ```

2. **Backend is ready** when you see:
   ```
   🚀 Clinical Trial Matcher API Server
   🔗 Base URL: http://localhost:5000
   ```

3. **Find your computer's IP address**:
   ```bash
   # Windows
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.1.100)
   
   # Mac/Linux
   ifconfig
   ```

4. **Use this as your API base URL**:
   ```
   http://192.168.1.100:5000
   ```

---

## Mobile App User Flow

### Screens to Build

1. **Login Screen**
   - Username and password input
   - "Login" button
   - Error message display

2. **Patient Dashboard**
   - Patient profile card (name, age, conditions)
   - List of matched trials (cards)
   - Filter controls (distance, phase)
   - Match score badges

3. **Trial Detail Screen**
   - Full trial information
   - Match explanation
   - Contact/save buttons (future)

### Design Mockups

**Login Screen**:
```
┌─────────────────────────┐
│  Clinical Trial Matcher │
│                         │
│  ┌───────────────────┐  │
│  │ Username          │  │
│  └───────────────────┘  │
│                         │
│  ┌───────────────────┐  │
│  │ Password          │  │
│  └───────────────────┘  │
│                         │
│  ┌───────────────────┐  │
│  │     LOGIN         │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

**Dashboard Screen**:
```
┌─────────────────────────┐
│ 👤 Sarah Chen    Logout │
├─────────────────────────┤
│ Age: 42 | Boston        │
│ 🏥 Breast Cancer        │
├─────────────────────────┤
│ Filters:                │
│ Distance: [50mi ▼]      │
│ Phase: [All ▼]          │
├─────────────────────────┤
│ 📊 18 Matched Trials    │
│                         │
│ ┌─────────────────────┐ │
│ │ 90% Match | 0 mi   │ │
│ │ Study of Drug X...  │ │
│ │ ✓ Breast Cancer    │ │
│ │ Phase 3            │ │
│ └─────────────────────┘ │
│                         │
│ ┌─────────────────────┐ │
│ │ 60% Match | 3 mi   │ │
│ │ Immunotherapy for...│ │
│ │ ✓ Breast Cancer    │ │
│ │ Phase 2            │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

---

## API Integration Examples

### React Native / TypeScript

#### 1. Setup API Client

```typescript
// api/client.ts
const API_BASE_URL = 'http://192.168.1.100:5000';  // Your computer's IP

export const api = {
  async login(username: string, password: string) {
    const response = await fetch(${API_BASE_URL}/login, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',  // Important for cookies
      body: JSON.stringify({ username, password })
    });
    return response.json();
  },

  async getPatientProfile() {
    const response = await fetch(${API_BASE_URL}/api/patient/me, {
      credentials: 'include'
    });
    return response.json();
  },

  async getMatches(patientId: number, filters?: { maxDistance?: number, phase?: string }) {
    const params = new URLSearchParams();
    if (filters?.maxDistance) params.append('max_distance', filters.maxDistance.toString());
    if (filters?.phase) params.append('phase', filters.phase);
    
    const response = await fetch(
      ${API_BASE_URL}/api/matches/?,
      { credentials: 'include' }
    );
    return response.json();
  },

  async getTrialDetails(trialId: number) {
    const response = await fetch(${API_BASE_URL}/api/trials/);
    return response.json();
  }
};
```

#### 2. Login Screen

```typescript
// screens/LoginScreen.tsx
import React, { useState } from 'react';
import { View, TextInput, Button, Text, Alert } from 'react-native';
import { api } from '../api/client';

export default function LoginScreen({ navigation }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async () => {
    try {
      const result = await api.login(username, password);
      
      if (result.success) {
        navigation.navigate('Dashboard');
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError('Network error. Is the backend running?');
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, marginBottom: 20 }}>Clinical Trial Matcher</Text>
      
      <TextInput
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        style={{ borderWidth: 1, padding: 10, marginBottom: 10 }}
      />
      
      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{ borderWidth: 1, padding: 10, marginBottom: 10 }}
      />
      
      {error ? <Text style={{ color: 'red' }}>{error}</Text> : null}
      
      <Button title="Login" onPress={handleLogin} />
      
      <Text style={{ marginTop: 20, fontSize: 12 }}>
        Demo users: sarah.chen, john.smith, maria.garcia{'\n'}
        Password: demo123
      </Text>
    </View>
  );
}
```

#### 3. Dashboard Screen

```typescript
// screens/DashboardScreen.tsx
import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, Picker } from 'react-native';
import { api } from '../api/client';

export default function DashboardScreen({ navigation }) {
  const [patient, setPatient] = useState(null);
  const [matches, setMatches] = useState([]);
  const [distance, setDistance] = useState(100);
  const [phase, setPhase] = useState('');

  useEffect(() => {
    loadData();
  }, [distance, phase]);

  const loadData = async () => {
    try {
      // Get patient profile
      const patientData = await api.getPatientProfile();
      setPatient(patientData);
      
      // Get matches
      const matchData = await api.getMatches(patientData.id, {
        maxDistance: distance,
        phase: phase || undefined
      });
      setMatches(matchData.matches);
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };

  const renderTrial = ({ item }) => (
    <TouchableOpacity
      style={{ padding: 15, borderWidth: 1, marginBottom: 10, borderRadius: 5 }}
      onPress={() => navigation.navigate('TrialDetail', { trialId: item.trial_id })}
    >
      <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
        <Text style={{ fontWeight: 'bold', color: getScoreColor(item.match_score) }}>
          {item.match_percentage} Match
        </Text>
        <Text>{item.distance_miles} miles | {item.phase}</Text>
      </View>
      <Text style={{ fontSize: 16, marginTop: 5 }}>{item.title}</Text>
      <Text style={{ color: 'green', marginTop: 5 }}>
        ✓ {item.matched_conditions.join(', ')}
      </Text>
    </TouchableOpacity>
  );

  const getScoreColor = (score) => {
    if (score >= 70) return 'green';
    if (score >= 40) return 'orange';
    return 'gray';
  };

  if (!patient) return <Text>Loading...</Text>;

  return (
    <View style={{ flex: 1, padding: 10 }}>
      {/* Patient Profile Card */}
      <View style={{ padding: 15, backgroundColor: '#f0f0f0', marginBottom: 10 }}>
        <Text style={{ fontSize: 20, fontWeight: 'bold' }}>{patient.name}</Text>
        <Text>Age: {patient.age} | {patient.city}</Text>
        <Text style={{ color: 'blue', marginTop: 5 }}>🏥 {patient.conditions}</Text>
      </View>

      {/* Filters */}
      <View style={{ flexDirection: 'row', marginBottom: 10 }}>
        <Picker
          selectedValue={distance}
          onValueChange={setDistance}
          style={{ flex: 1 }}
        >
          <Picker.Item label="10 miles" value={10} />
          <Picker.Item label="25 miles" value={25} />
          <Picker.Item label="50 miles" value={50} />
          <Picker.Item label="100 miles" value={100} />
        </Picker>

        <Picker
          selectedValue={phase}
          onValueChange={setPhase}
          style={{ flex: 1 }}
        >
          <Picker.Item label="All Phases" value="" />
          <Picker.Item label="Phase 1" value="PHASE1" />
          <Picker.Item label="Phase 2" value="PHASE2" />
          <Picker.Item label="Phase 3" value="PHASE3" />
          <Picker.Item label="Phase 4" value="PHASE4" />
        </Picker>
      </View>

      {/* Matched Trials */}
      <Text style={{ fontSize: 18, marginBottom: 10 }}>
        📊 {matches.length} Matched Trials
      </Text>

      <FlatList
        data={matches}
        renderItem={renderTrial}
        keyExtractor={(item) => item.trial_id.toString()}
      />
    </View>
  );
}
```

#### 4. Trial Detail Screen

```typescript
// screens/TrialDetailScreen.tsx
import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView } from 'react-native';
import { api } from '../api/client';

export default function TrialDetailScreen({ route }) {
  const { trialId } = route.params;
  const [trial, setTrial] = useState(null);

  useEffect(() => {
    api.getTrialDetails(trialId).then(setTrial);
  }, [trialId]);

  if (!trial) return <Text>Loading...</Text>;

  return (
    <ScrollView style={{ padding: 15 }}>
      <Text style={{ fontSize: 20, fontWeight: 'bold', marginBottom: 10 }}>
        {trial.title}
      </Text>

      <View style={{ backgroundColor: '#e8f4f8', padding: 10, marginBottom: 10 }}>
        <Text><Text style={{ fontWeight: 'bold' }}>NCT ID:</Text> {trial.nct_id}</Text>
        <Text><Text style={{ fontWeight: 'bold' }}>Phase:</Text> {trial.phase}</Text>
        <Text><Text style={{ fontWeight: 'bold' }}>Status:</Text> {trial.status}</Text>
      </View>

      <Text style={{ fontSize: 16, fontWeight: 'bold', marginTop: 10 }}>Location</Text>
      <Text>{trial.city} ({trial.distance_from_boston} miles from Boston)</Text>

      <Text style={{ fontSize: 16, fontWeight: 'bold', marginTop: 10 }}>Conditions</Text>
      <Text>{trial.conditions}</Text>

      <Text style={{ fontSize: 16, fontWeight: 'bold', marginTop: 10 }}>Age Eligibility</Text>
      <Text>Ages {trial.min_age} - {trial.max_age}</Text>
    </ScrollView>
  );
}
```

---

## Testing Tips

### 1. Test with cURL first

```bash
# Login
curl -X POST http://192.168.1.100:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"sarah.chen","password":"demo123"}' \
  -c cookies.txt

# Get matches (using saved cookie)
curl http://192.168.1.100:5000/api/matches/1 -b cookies.txt
```

### 2. Use Postman Collection

Import these endpoints into Postman:
- POST /login - Body: {"username":"sarah.chen","password":"demo123"}
- GET /api/patient/me
- GET /api/matches/1?max_distance=50
- GET /api/trials/1

### 3. Sample Patient IDs

| ID | Username | Name | Conditions |
|----|----------|------|------------|
| 1 | sarah.chen | Sarah Chen | Breast Cancer |
| 2 | john.smith | John Smith | Diabetes, Hypertension |
| 3 | maria.garcia | Maria Garcia | COPD, Heart Disease |
| 4 | david.lee | David Lee | Depression, Anxiety |
| 5 | emily.brown | Emily Brown | Multiple Sclerosis |

---

## Common Issues

### 1. Network Error

**Problem**: etch failed or Network request failed

**Solution**:
- Make sure backend is running (python app.py)
- Use your computer's IP address, not localhost
- Both devices on same WiFi network
- Check firewall settings

### 2. CORS Error

**Solution**: CORS is enabled in the backend. If you still have issues, check the browser console.

### 3. Cookie Not Saving

**Solution**: Make sure you use credentials: 'include' in fetch calls.

---

## Color Scheme Suggestions

- **Primary**: #2196F3 (Blue)
- **Secondary**: #4CAF50 (Green)
- **High Match**: #4CAF50 (Green)
- **Medium Match**: #FF9800 (Orange)
- **Low Match**: #9E9E9E (Gray)
- **Background**: #F5F5F5 (Light Gray)

---

## Quick Win Features

1. **Pull to Refresh**: Reload matches on dashboard
2. **Match Score Badge**: Color-coded score (green/orange/gray)
3. **Search Bar**: Filter trials by keyword
4. **Patient Switcher**: Dropdown to demo different patients
5. **Loading States**: Spinners while fetching data

---

## Need Help?

1. **Backend not working?** Ask backend team
2. **API questions?** Check API_DOCUMENTATION.md
3. **Sample data?** All patients use password demo123

---

**Ready to build!** 🚀 Start with the login screen and work your way up.
