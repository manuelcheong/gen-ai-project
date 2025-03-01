// import logo from './logo.svg';
import './App.css';
import { Card, CardContent } from "./components/ui/card";
import { Button } from "./components/ui/button";

const menu = [
  {
    category: "Entradas",
    items: [
      { name: "Bruschetta", description: "Pan tostado con tomate y albahaca.", price: "$5.00", image: "https://source.unsplash.com/200x200/?bruschetta" },
      { name: "Calamares fritos", description: "Acompañados de salsa tártara.", price: "$8.00", image: "https://source.unsplash.com/200x200/?calamari" },
    ],
  },
  {
    category: "Platos Fuertes",
    items: [
      { name: "Lomo Saltado", description: "Carne salteada con papas y arroz.", price: "$12.00", image: "https://source.unsplash.com/200x200/?steak" },
      { name: "Pasta Alfredo", description: "Fettuccine con salsa cremosa de queso.", price: "$10.00", image: "https://source.unsplash.com/200x200/?pasta" },
    ],
  },
  {
    category: "Postres",
    items: [
      { name: "Tiramisú", description: "Postre italiano con café y mascarpone.", price: "$6.00", image: "https://source.unsplash.com/200x200/?tiramisu" },
      { name: "Cheesecake", description: "Tarta de queso con frutos rojos.", price: "$6.50", image: "https://source.unsplash.com/200x200/?cheesecake" },
    ],
  },
];

function App() {
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">Menú del Restaurante</h1>
      {menu.map((section) => (
        <div key={section.category} className="mb-6">
          <h2 className="text-xl font-semibold mb-4">{section.category}</h2>
          {section.items.map((item) => (
            <Card key={item.name} className="mb-4 p-4 flex items-center">
              <img src={item.image} alt={item.name} className="w-20 h-20 rounded-lg mr-4" />
              <CardContent className="flex-1">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-medium">{item.name}</h3>
                    <p className="text-sm text-gray-600">{item.description}</p>
                  </div>
                  <span className="font-bold text-green-600">{item.price}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ))}
      <div className="text-center mt-6">
        <Button className="bg-blue-500 text-white px-4 py-2 rounded-lg">Ordenar Ahora</Button>
      </div>
    </div>
  );
  /* return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  ); */
}

export default App;
