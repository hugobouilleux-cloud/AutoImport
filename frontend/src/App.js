import { useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, CheckCircle2, XCircle, Link2 } from "lucide-react";
import { toast } from "sonner";
import { Toaster } from "@/components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [formData, setFormData] = useState({
    site_url: "",
    login: "",
    password: ""
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [savedConnections, setSavedConnections] = useState([]);
  const [navigating, setNavigating] = useState(false);
  const [adminUrl, setAdminUrl] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const testConnection = async () => {
    if (!formData.site_url || !formData.login || !formData.password) {
      toast.error("Veuillez remplir tous les champs");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${API}/connection/test`, formData);
      setResult(response.data);
      
      if (response.data.success) {
        toast.success("Connexion réussie !");
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      console.error("Error testing connection:", error);
      setResult({
        success: false,
        message: "Erreur lors du test de connexion"
      });
      toast.error("Erreur lors du test de connexion");
    } finally {
      setLoading(false);
    }
  };

  const saveConnection = async () => {
    if (!formData.site_url || !formData.login || !formData.password) {
      toast.error("Veuillez remplir tous les champs");
      return;
    }

    try {
      await axios.post(`${API}/connection/save`, formData);
      toast.success("Configuration sauvegardée avec succès");
      setFormData({ site_url: "", login: "", password: "" });
      setResult(null);
      loadConnections();
    } catch (error) {
      console.error("Error saving connection:", error);
      toast.error("Erreur lors de la sauvegarde");
    }
  };

  const loadConnections = async () => {
    try {
      const response = await axios.get(`${API}/connection/list`);
      setSavedConnections(response.data);
    } catch (error) {
      console.error("Error loading connections:", error);
    }
  };

  const deleteConnection = async (id) => {
    try {
      await axios.delete(`${API}/connection/${id}`);
      toast.success("Connexion supprimée");
      loadConnections();
    } catch (error) {
      console.error("Error deleting connection:", error);
      toast.error("Erreur lors de la suppression");
    }
  };

  const navigateToAdmin = async () => {
    if (!formData.site_url || !formData.login || !formData.password) {
      toast.error("Veuillez remplir tous les champs");
      return;
    }

    setNavigating(true);
    setAdminUrl(null);

    try {
      const response = await axios.post(`${API}/connection/navigate-admin`, formData);
      
      if (response.data.success) {
        toast.success("Navigation vers l'administration réussie !");
        setAdminUrl(response.data.admin_url);
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      console.error("Error navigating to admin:", error);
      toast.error("Erreur lors de la navigation");
    } finally {
      setNavigating(false);
    }
  };

  return (
    <div className="min-h-screen" data-testid="home-page">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="border-b backdrop-blur-sm bg-white/70 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg">
              <Link2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AutoConnect</h1>
              <p className="text-sm text-gray-500">Automatisez vos connexions</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        <div className="max-w-2xl mx-auto space-y-8">
          {/* Connection Form Card */}
          <Card className="border-0 shadow-xl" data-testid="connection-form">
            <CardHeader className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-t-lg">
              <CardTitle className="text-2xl text-gray-900">Configuration de connexion</CardTitle>
              <CardDescription className="text-gray-600">
                Entrez les informations pour vous connecter au site cible
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              <div className="space-y-2">
                <Label htmlFor="site_url" className="text-gray-700 font-medium">URL du site</Label>
                <Input
                  id="site_url"
                  name="site_url"
                  type="url"
                  placeholder="https://example.com/ng/login/"
                  value={formData.site_url}
                  onChange={handleInputChange}
                  className="h-11"
                  data-testid="site-url-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="login" className="text-gray-700 font-medium">Identifiant</Label>
                <Input
                  id="login"
                  name="login"
                  type="text"
                  placeholder="Votre identifiant"
                  value={formData.login}
                  onChange={handleInputChange}
                  className="h-11"
                  data-testid="login-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-700 font-medium">Mot de passe</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Votre mot de passe"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="h-11"
                  data-testid="password-input"
                />
              </div>

              {result && (
                <Alert
                  className={`${result.success ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-200'}`}
                  data-testid="connection-result"
                >
                  <div className="flex items-center gap-2">
                    {result.success ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600" />
                    )}
                    <AlertDescription className={`${result.success ? 'text-emerald-700' : 'text-red-700'}`}>
                      {result.message}
                    </AlertDescription>
                  </div>
                </Alert>
              )}

              <div className="flex gap-3 pt-2">
                <Button
                  onClick={testConnection}
                  disabled={loading}
                  className="flex-1 h-11 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-medium shadow-md hover:shadow-lg transition-all"
                  data-testid="test-connection-button"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Test en cours...
                    </>
                  ) : (
                    "Tester la connexion"
                  )}
                </Button>
                <Button
                  onClick={saveConnection}
                  variant="outline"
                  className="flex-1 h-11 border-2 border-emerald-500 text-emerald-600 hover:bg-emerald-50 font-medium transition-colors"
                  data-testid="save-connection-button"
                >
                  Sauvegarder
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Info Card */}
          <Card className="border-l-4 border-l-teal-400 bg-gradient-to-br from-slate-50 to-gray-50 shadow-md">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-teal-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-lg">💡</span>
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold text-gray-900">Comment ça marche ?</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>1. Entrez l'URL de connexion du site cible</li>
                    <li>2. Saisissez vos identifiants de connexion</li>
                    <li>3. Testez la connexion avant de sauvegarder</li>
                    <li>4. Sauvegardez pour utiliser plus tard</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;